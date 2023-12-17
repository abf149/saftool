package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class ScalarTagComparatorArray(numTags: Int, tagBitWidth: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val tagQuery = Input(UInt(tagBitWidth.W))
    val lookupTrigger = Input(Bool())
    val ignoreTags = Input(Vec(numTags, Bool())) // Vector of bits to ignore specific tags
    val tagMemoryInterface = Input(Vec(numTags, UInt(tagBitWidth.W))) // Interface to memory tags
    val matchOutputs = Output(Vec(numTags, Bool())) // Outputs showing matches
  })

  // Combinational logic for tag comparison
  for (i <- 0 until numTags) {
    when(io.enable && io.lookupTrigger && !io.ignoreTags(i)) {
      io.matchOutputs(i) := io.tagQuery < io.tagMemoryInterface(i)
    } .otherwise {
      io.matchOutputs(i) := false.B
    }
  }
}
