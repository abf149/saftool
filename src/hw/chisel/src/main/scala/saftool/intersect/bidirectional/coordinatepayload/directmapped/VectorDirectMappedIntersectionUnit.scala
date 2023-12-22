package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class VectorDirectMappedIntersectionUnit(val vectorLength: Int, val fiberLength: Int, val tagBitWidth: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val list1 = Input(Vec(vectorLength, UInt(tagBitWidth.W)))
    val list2 = Input(Vec(vectorLength, UInt(tagBitWidth.W)))
    val commonElements = Output(Vec(vectorLength, UInt(tagBitWidth.W)))
    val numMatches = Output(UInt(log2Ceil(vectorLength + 1).W))
  })

  val bitmask1 = Wire(Vec(fiberLength, Bool()))
  val bitmask2 = Wire(Vec(fiberLength, Bool()))
  val commonBitmask = Wire(Vec(fiberLength, Bool()))
  commonBitmask := VecInit(Seq.fill(fiberLength)(false.B)) // Default initialization

  // Default assignment for outputs
  io.commonElements := VecInit(Seq.fill(vectorLength)(0.U(tagBitWidth.W)))
  io.numMatches := 0.U

  when(io.enable) {
    // Reset and set bits in the bitmask based on list values
    for(i <- 0 until fiberLength) {
      bitmask1(i) := false.B
      bitmask2(i) := false.B
    }

    for(i <- 0 until vectorLength) {
      bitmask1(io.list1(i)) := true.B
      bitmask2(io.list2(i)) := true.B
    }

    // Bitwise AND Operation
    for(i <- 0 until fiberLength) {
      commonBitmask(i) := bitmask1(i) & bitmask2(i)
    }

    // Parallel Prefix Sum
    val prefixSumModule = Module(new BitmaskParallelKoggeStonePrefixSumCombinational(fiberLength))
    prefixSumModule.input.bitmask := commonBitmask.asUInt
    val prefixSums = prefixSumModule.output.sums

    // Compaction Logic
    val tempCommonElements = VecInit(Seq.fill(vectorLength)(0.U(tagBitWidth.W)))
    //var matchCount = 0.U
    val matchCount = Wire(Vec(fiberLength + 1, UInt(log2Ceil(vectorLength + 1).W)))
    matchCount(0) := 0.U
    for(i <- 0 until fiberLength) {
      matchCount(i + 1) := prefixSums(i)
    }
    
    for(i <- 0 until fiberLength) {
      when(commonBitmask(i)) {
        tempCommonElements(matchCount(i)) := i.U
      //  matchCount(i + 1) := matchCount(i) + 1.U
      }
      //.otherwise{
      //  matchCount(i + 1) := matchCount(i)
      //}
    }

    // Output Assignment
    for(i <- 0 until vectorLength) {
      io.commonElements(i) := Mux(i.U < matchCount(fiberLength), tempCommonElements(i), 0.U)
    }

    // Output the number of matches
    io.numMatches := matchCount(fiberLength)
  }.otherwise {
    // Reset bitmasks when not enabled
    for(i <- 0 until fiberLength) {
      bitmask1(i) := false.B
      bitmask2(i) := false.B
    }

    io.commonElements := VecInit(Seq.fill(vectorLength)(0.U(tagBitWidth.W)))
    io.numMatches := 0.U
  }
}