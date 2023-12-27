package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class VectorTwoFingerMergeIntersectionRegistered(val metaDataWidth: Int, val arraySize: Int) extends Module with RequireSyncReset {
  val M = 2 * arraySize - 1
  val headWidth = log2Ceil(arraySize) + 1

  val io = IO(new Bundle {
    // Inputs
    val enable_in = Input(Bool())
    val inputWireArrays = Input(Vec(2, Vec(arraySize, UInt(metaDataWidth.W))))

    // Outputs
    val enable_out = Output(Bool())
    val outputWireArrays = Output(Vec(arraySize, UInt(metaDataWidth.W)))
    val num_matches = Output(UInt(log2Ceil(M + 1).W))
  })

  val core = Module(new VectorTwoFingerMergeIntersection(metaDataWidth, arraySize))

  // Input Registers
  val enable_in_reg = RegNext(io.enable_in)
  val inputWireArrays_reg = Reg(Vec(2, Vec(arraySize, UInt(metaDataWidth.W))))
  for(i <- 0 until 2; j <- 0 until arraySize) {
    inputWireArrays_reg(i)(j) := RegNext(io.inputWireArrays(i)(j))
  }

  // Connect the registered inputs to the core component
  core.io.enable_in := enable_in_reg
  core.io.inputWireArrays := inputWireArrays_reg

  // Output Registers
  val enable_out_reg = RegNext(core.io.enable_out)
  val outputWireArrays_reg = Reg(Vec(arraySize, UInt(metaDataWidth.W)))
  val num_matches_reg = RegNext(core.io.num_matches)
  for(i <- 0 until arraySize) {
    outputWireArrays_reg(i) := RegNext(core.io.outputWireArrays(i))
  }

  // Connect the registered outputs to the IO
  io.enable_out := enable_out_reg
  io.outputWireArrays := outputWireArrays_reg
  io.num_matches := num_matches_reg
}
