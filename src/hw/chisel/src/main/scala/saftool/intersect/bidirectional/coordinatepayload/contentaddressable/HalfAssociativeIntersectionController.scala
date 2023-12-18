package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class HalfAssociativeIntersectionController(val numTags: Int, val tagBitWidth: Int) extends Module with RequireSyncReset {
  require(isPow2(numTags), "Number of tags must be a power of 2")

  val io = IO(new Bundle {
    val tagInput = Input(UInt(tagBitWidth.W))
    val triggerInput = Input(Bool())
    val enable = Input(Bool())
    val disableComparatorMask = Input(UInt(numTags.W))
    val memoryLookupAddress = Output(UInt(log2Ceil(numTags).W))
    val memoryLookupEnable = Output(Bool())
    val disableNextStageMask = Output(UInt(numTags.W))
    val tagMemoryInterface = Input(Vec(numTags, UInt(tagBitWidth.W)))
    val isMatch = Output(Bool())

    val memWriteEnable = Output(Bool())
    val memWriteData = Output(Vec(numTags, UInt(tagBitWidth.W)))
    val memPingpongSelect = Output(Bool())

    val writeEnable = Input(Bool())
    val writeData = Input(Vec(numTags, UInt(tagBitWidth.W)))
    val pingpongSelect = Input(Bool())

    val memReadTag = Input(UInt(tagBitWidth.W))
    val peek_out = Output(UInt(tagBitWidth.W))

    val force_peek = Input(Bool())
    val head_in = Input(UInt(log2Ceil(numTags).W))
    val head_out = Output(UInt(log2Ceil(numTags).W))

    val is_empty = Output(Bool())
  })

  val tagComparatorArray = Module(new ScalarTagComparatorArray(numTags, tagBitWidth))
  val priorityEncoder = Module(new ParallelDec2PriorityEncoderPrefixOr(numTags))

  // Calculate is_empty condition
  val headInTooLarge = io.head_in > (numTags.U - 1.U)
  val noMatchWhenNotForcePeek = !io.force_peek && !io.isMatch
  io.is_empty := headInTooLarge || noMatchWhenNotForcePeek

  // Default initialization for outputs and internal signals
  io.memoryLookupAddress := 0.U
  io.memoryLookupEnable := false.B
  io.disableNextStageMask := 0.U
  io.isMatch := false.B
  io.peek_out := 0.U
  io.head_out := 0.U

  // Default initialization for inputs to submodules
  tagComparatorArray.io.enable := io.enable
  tagComparatorArray.io.tagQuery := io.tagInput
  tagComparatorArray.io.lookupTrigger := io.triggerInput
  tagComparatorArray.io.ignoreTags := io.disableComparatorMask.asBools
  tagComparatorArray.io.tagMemoryInterface := io.tagMemoryInterface
  priorityEncoder.io.enable := io.enable
  priorityEncoder.io.in := tagComparatorArray.io.matchOutputs.asUInt

  // Conditional logic
  when(io.enable) {
    when(io.force_peek) {
      // When force_peek is high and the module is enabled
      io.peek_out := io.tagMemoryInterface(io.head_in)
      io.head_out := io.head_in + 1.U
      val maskWithHeadBitSet = io.disableComparatorMask | UIntToOH(io.head_in, numTags)
      io.disableNextStageMask := maskWithHeadBitSet
    } .elsewhen(headInTooLarge) {
      // Logic when is_empty is true *due to headInTooLarge*
      io.peek_out := 0.U
      io.head_out := io.head_in
      io.disableNextStageMask := io.disableComparatorMask
      io.memoryLookupEnable := true.B
    } .otherwise {
      // Normal operation
      io.memoryLookupAddress := priorityEncoder.io.out.priorityIdx
      io.memoryLookupEnable := priorityEncoder.io.out.valid && io.triggerInput && io.enable
      io.disableNextStageMask := priorityEncoder.io.out.prefixOrOut | io.disableComparatorMask
      io.isMatch := priorityEncoder.io.out.valid
      io.head_out := io.memoryLookupAddress
      io.peek_out := io.memReadTag
    }
  } .otherwise {
    // Module is disabled
    // Keep default values
  }

  // Wiring for additional and mirror interfaces
  io.memWriteEnable := io.writeEnable
  io.memWriteData := io.writeData
  io.memPingpongSelect := io.pingpongSelect
}
