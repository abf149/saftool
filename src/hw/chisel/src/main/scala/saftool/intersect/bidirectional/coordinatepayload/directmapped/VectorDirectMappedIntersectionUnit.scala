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
  val tempCommonElements = Wire(Vec(fiberLength, UInt(tagBitWidth.W)))
  //val matchCount = Wire(UInt(log2Ceil(fiberLength + 1).W))

  when(io.enable) {
    // Initialize and set bits in the bitmask based on list values
    bitmask1 := VecInit(Seq.fill(fiberLength)(false.B))
    bitmask2 := VecInit(Seq.fill(fiberLength)(false.B))
    //matchCount := 0.U

    for(i <- 0 until vectorLength) {
      bitmask1(io.list1(i)) := true.B
      bitmask2(io.list2(i)) := true.B
    }

    // Bitwise AND Operation
    val commonBitmask = Wire(Vec(fiberLength, Bool()))
    for(i <- 0 until fiberLength) {
      commonBitmask(i) := bitmask1(i) & bitmask2(i)
    }

    // Parallel Prefix Sum
    val prefixSumModule = Module(new ParallelKoggeStonePrefixSumCombinational(fiberLength))
    prefixSumModule.input.bitmask := commonBitmask.asUInt
    val prefixSums = prefixSumModule.output.sums

    // Compaction Logic
    //val tempCommonElements = VecInit(Seq.fill(fiberLength)(0.U(tagBitWidth.W)))
    //var matchCount = 0.U
    for(i <- 0 until fiberLength) {
      when(commonBitmask(i)) {
        tempCommonElements(prefixSums(i)) := i.U
        //matchCount = matchCount + 1.U
      }
    }

    // Output Assignment
    for(i <- 0 until vectorLength) {
      io.commonElements(i) := Mux(i.U < prefixSums(vectorLength-1), tempCommonElements(i), 0.U)
    }

    // Output the number of matches
    io.numMatches := prefixSums(vectorLength-1)
  }.otherwise {
    // Assign default values when not enabled
    io.commonElements := VecInit(Seq.fill(vectorLength)(0.U(tagBitWidth.W)))
    io.numMatches := 0.U
  }
}