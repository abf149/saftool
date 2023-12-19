package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class VectorSkipAheadIntersectionUnit(val vectorLength: Int, val numTags: Int, val tagBitWidth: Int) extends Module with RequireSyncReset {
  require(isPow2(numTags), "Number of tags must be a power of 2")

  val io = IO(new Bundle {
    // Mirrored interfaces for Left and Right
    val left_disableComparatorMask = Input(UInt(numTags.W))
    val right_disableComparatorMask = Input(UInt(numTags.W))
    val left_head_in = Input(UInt(log2Ceil(numTags).W))
    val right_head_in = Input(UInt(log2Ceil(numTags).W))
    val left_disableNextStageMask = Output(UInt(numTags.W))
    val right_disableNextStageMask = Output(UInt(numTags.W))
    val left_head_out = Output(UInt(log2Ceil(numTags).W))
    val right_head_out = Output(UInt(log2Ceil(numTags).W))
    val left_is_empty = Output(Bool())
    val right_is_empty = Output(Bool())

    // Write interfaces for Left and Right memories
    val left_writeEnable = Input(Bool())
    val right_writeEnable = Input(Bool())
    val left_writeData = Input(Vec(numTags, UInt(tagBitWidth.W)))
    val right_writeData = Input(Vec(numTags, UInt(tagBitWidth.W)))

    // Interfaces for Out memory
    val readEnable = Input(Bool())
    val readData = Output(Vec(vectorLength, UInt(tagBitWidth.W)))

    // General control interfaces
    val enable = Input(Bool())
    val skip_from_in = Input(Bool())
    val skip_from_out = Output(Bool())
    val pingpongSelect = Input(Bool())

    val is_match = Output(Bool())
    val match_tag = Output(UInt(tagBitWidth.W))

    val num_matches = Output(UInt(log2Ceil(vectorLength + 1).W))    
  })

  val leftMemory = Module(new VectorFillGatherReadMemory(tagBitWidth, numTags, vectorLength))
  val rightMemory = Module(new VectorFillGatherReadMemory(tagBitWidth, numTags, vectorLength))
  val outMemory = Module(new VectorReadScatterWriteMemory(tagBitWidth, vectorLength, vectorLength))
  val daisyChain = VecInit(Seq.fill(vectorLength)(Module(new SkipAheadIntersectionController(numTags, tagBitWidth)).io))

  // Wiring for memories and controllers
  leftMemory.io.enable := io.enable
  rightMemory.io.enable := io.enable
  outMemory.io.enable := io.enable
  outMemory.io.readEnable := io.readEnable
  io.readData := outMemory.io.readData

  leftMemory.io.writeEnable := io.left_writeEnable
  rightMemory.io.writeEnable := io.right_writeEnable
  leftMemory.io.writeData := io.left_writeData
  rightMemory.io.writeData := io.right_writeData

  leftMemory.io.pingpongSelect := io.pingpongSelect
  rightMemory.io.pingpongSelect := io.pingpongSelect
  outMemory.io.pingpongSelect := io.pingpongSelect

  // Daisy chain logic
  val matchCount = Wire(Vec(vectorLength + 1, UInt(log2Ceil(vectorLength + 1).W)))
  matchCount(0) := 0.U

  for (i <- 0 until vectorLength) {
    val stage = daisyChain(i)
    val nextStage = if (i < vectorLength - 1) daisyChain(i + 1) else null

    // Wire up the stage interfaces
    stage.enable := io.enable && (if (i > 0) !daisyChain(i - 1).left.is_empty && !daisyChain(i - 1).right.is_empty else true.B)
    stage.skip_from_in := io.skip_from_in
    stage.left.disableComparatorMask := (if (i == 0) io.left_disableComparatorMask else daisyChain(i - 1).left.disableNextStageMask)
    stage.right.disableComparatorMask := (if (i == 0) io.right_disableComparatorMask else daisyChain(i - 1).right.disableNextStageMask)
    stage.left.head_in := (if (i == 0) io.left_head_in else daisyChain(i - 1).left.head_out)
    stage.right.head_in := (if (i == 0) io.right_head_in else daisyChain(i - 1).right.head_out)

    // Wire up memory interfaces
    stage.left.tagMemoryInterface := leftMemory.io.directRegisterOutputs
    stage.left.memReadTag := leftMemory.io.readData(i)
    stage.left.memoryLookupAddress := leftMemory.io.readAddresses(i)
    stage.left.memoryLookupEnable := leftMemory.io.readEnable(i)

    stage.right.tagMemoryInterface := rightMemory.io.directRegisterOutputs
    stage.right.memReadTag := rightMemory.io.readData(i)
    stage.right.memoryLookupAddress := rightMemory.io.readAddresses(i)
    stage.right.memoryLookupEnable := rightMemory.io.readEnable(i)

    // Wire up Out memory write logic
    outMemory.io.writeAddresses(i) := matchCount(i)
    outMemory.io.writeEnable(i) := stage.is_match
    outMemory.io.writeData(i) := stage.match_tag

    // Compute the match count
    matchCount(i + 1) := matchCount(i) + stage.is_match.asUInt

    // Bypass logic for is_empty condition
    when(stage.left.is_empty || stage.right.is_empty) {
      for (j <- i + 1 until vectorLength) {
        daisyChain(j).enable := false.B
      }
      if (nextStage != null) {
        io.left_disableNextStageMask := stage.left.disableNextStageMask
        io.right_disableNextStageMask := stage.right.disableNextStageMask
        io.left_head_out := stage.left.head_out
        io.right_head_out := stage.right.head_out
        io.left_is_empty := stage.left.is_empty
        io.right_is_empty := stage.right.is_empty
      }
    }
  }

  // Outputs for the last stage
  val lastStage = daisyChain(vectorLength - 1)
  io.skip_from_out := lastStage.skip_from_out
  io.is_match := lastStage.is_match
  io.match_tag := lastStage.match_tag
  io.num_matches := matchCount(vectorLength)
}
