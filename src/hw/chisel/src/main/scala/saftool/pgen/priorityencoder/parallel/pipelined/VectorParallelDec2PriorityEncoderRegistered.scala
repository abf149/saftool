package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class VectorParallelDec2PriorityEncoderRegistered(val vectorLength: Int, val inputbits: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val input = Input(UInt(inputbits.W))
    val outputs = Output(Vec(vectorLength, UInt(log2Ceil(inputbits).W)))
    val bitmask_next = Output(UInt(inputbits.W))
    val num_valid = Output(UInt((log2Ceil(inputbits)+1).W))
    val is_done = Output(Bool())
  })

  val combinatorialComponent = Module(new VectorParallelDec2PriorityEncoder(vectorLength, inputbits))

  // Input Registers
  val enable_reg = RegNext(io.enable, init = false.B)
  val input_reg = RegNext(io.input, init = 0.U(inputbits.W))

  // Connect the registered inputs to the combinatorial component
  combinatorialComponent.io.enable := enable_reg
  combinatorialComponent.io.input := input_reg

  // Output Registers
  val outputs_reg = Reg(Vec(vectorLength, UInt(log2Ceil(inputbits).W)))
  val bitmask_next_reg = Reg(UInt(inputbits.W))
  val num_valid_reg = Reg(UInt((log2Ceil(inputbits)+1).W))
  val is_done_reg = Reg(Bool())

  // Connect the combinatorial outputs to the registered outputs
  outputs_reg := combinatorialComponent.io.outputs
  bitmask_next_reg := combinatorialComponent.io.bitmask_next
  num_valid_reg := combinatorialComponent.io.num_valid
  is_done_reg := combinatorialComponent.io.is_done

  // Connect the registered outputs to the IO
  io.outputs := outputs_reg
  io.bitmask_next := bitmask_next_reg
  io.num_valid := num_valid_reg
  io.is_done := is_done_reg
}