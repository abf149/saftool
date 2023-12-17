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
    val isMatch = Output(Bool()) // Added "isMatch" output
  })

  val tagComparatorArray = Module(new ScalarTagComparatorArray(numTags, tagBitWidth))
  val priorityEncoder = Module(new ParallelDec2PriorityEncoderPrefixOr(numTags))

  // Wiring
  tagComparatorArray.io.enable := io.enable
  tagComparatorArray.io.tagQuery := io.tagInput
  tagComparatorArray.io.lookupTrigger := io.triggerInput
  tagComparatorArray.io.ignoreTags := io.disableComparatorMask.asBools
  tagComparatorArray.io.tagMemoryInterface := io.tagMemoryInterface // Wire the memory interface

  priorityEncoder.io.enable := io.enable
  priorityEncoder.io.in := tagComparatorArray.io.matchOutputs.asUInt

  // Output wiring
  io.memoryLookupAddress := priorityEncoder.io.out.priorityIdx
  io.memoryLookupEnable := priorityEncoder.io.out.valid && io.triggerInput && io.enable
  io.disableNextStageMask := priorityEncoder.io.out.prefixOrOut | io.disableComparatorMask
  io.isMatch := priorityEncoder.io.out.valid // Set "isMatch" to the valid output of the priority encoder
}

