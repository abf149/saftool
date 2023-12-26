package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class VectorDirectMappedIntersectionUnitRegistered(val vectorLength: Int, val fiberLength: Int, val tagBitWidth: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val list1 = Input(Vec(vectorLength, UInt(tagBitWidth.W)))
    val list2 = Input(Vec(vectorLength, UInt(tagBitWidth.W)))
    val commonElements = Output(Vec(vectorLength, UInt(tagBitWidth.W)))
    val numMatches = Output(UInt(log2Ceil(vectorLength + 1).W))
  })

  val core = Module(new VectorDirectMappedIntersectionUnit(vectorLength, fiberLength, tagBitWidth))

  // Input Registers
  val enable_reg = RegNext(io.enable)
  val list1_reg = Reg(Vec(vectorLength, UInt(tagBitWidth.W)))
  val list2_reg = Reg(Vec(vectorLength, UInt(tagBitWidth.W)))
  for(i <- 0 until vectorLength) {
    list1_reg(i) := RegNext(io.list1(i))
    list2_reg(i) := RegNext(io.list2(i))
  }

  // Connect the registered inputs to the core component
  core.io.enable := enable_reg
  core.io.list1 := list1_reg
  core.io.list2 := list2_reg

  // Output Registers
  val commonElements_reg = Reg(Vec(vectorLength, UInt(tagBitWidth.W)))
  val numMatches_reg = Reg(UInt(log2Ceil(vectorLength + 1).W))
  for(i <- 0 until vectorLength) {
    commonElements_reg(i) := RegNext(core.io.commonElements(i))
  }
  numMatches_reg := RegNext(core.io.numMatches)

  // Connect the registered outputs to the IO
  io.commonElements := commonElements_reg
  io.numMatches := numMatches_reg
}
