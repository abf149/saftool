package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Registered interface wrapped around combinatorial parallel priority encoder */
class ParallelDec2PriorityEncoderRegistered(val inputbits: Int) extends Module with RequireSyncReset {
  val output_bits = (log10(inputbits)/log10(2.0)).toInt

  val input = IO(new Bundle{val in = Input(UInt(inputbits.W))})
  val output = IO(new PriorityEncoderBundle(output_bits))
  val input_reg = RegInit(0.U)
  val output_idx_reg = RegInit(0.U) 
  val output_vld_reg = RegInit(0.U)

  // Combinational unit (TODO: typo)
  val combinatorial_penc = Module(new ParallelDec2PriorityEncoderCombinational(inputbits))

  input_reg := input.in
  combinatorial_penc.input.in := input_reg
  output_idx_reg := combinatorial_penc.output.idx
  output_vld_reg := combinatorial_penc.output.vld 
  output.idx := output_idx_reg
  output.vld := output_vld_reg
}

