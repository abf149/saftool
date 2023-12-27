package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Priority encoder first stage - takes two "0-bit" inputs each with a valid signal, outputs 1-bit index with valid signal */
class ParallelDec2PriorityEncoderBaseCombinational() extends Module   with RequireSyncReset {
  val input0 = IO(new Bundle{val vld = Input(UInt(1.W))})
  val input1 = IO(new Bundle{val vld = Input(UInt(1.W))})
  val output = IO(new PriorityEncoderBundle(1))

  output.vld := (input0.vld.asBool || input1.vld.asBool).asUInt
  output.idx := input1.vld
}

/* Priority encoder intermediate stage - takes two n-bit inputs each with a valid signal, outputs n+1-bit index with valid signl */
class ParallelDec2PriorityEncoderStageCombinational(val bitwidth: Int) extends Module   with RequireSyncReset {
  val input0 = IO(Flipped(new PriorityEncoderBundle(bitwidth)))
  val input1 = IO(Flipped(new PriorityEncoderBundle(bitwidth)))
  val output = IO(new PriorityEncoderBundle(bitwidth+1))

  output.vld := (input0.vld.asBool || input1.vld.asBool).asUInt
  output.idx := Mux(input1.vld.asBool,Cat(input1.vld,input1.idx),Cat(input1.vld,input0.idx))
}

class ParallelDec2PriorityEncoderCombinational(val inputbits: Int) extends Module with RequireSyncReset {
  val output_bits = (log10(inputbits)/log10(2.0)).toInt

  val input = IO(new Bundle{val in = Input(UInt(inputbits.W))})
  val output = IO(new PriorityEncoderBundle(output_bits))

  def doBuild(base_offset: Int, cur_inputbits: Int, cur_output: PriorityEncoderBundle): Unit =
    //val new_inputbits = (cur_inputbits/2).toInt 

    

    if (cur_inputbits > 0) {
      val stage_penc = Module(new ParallelDec2PriorityEncoderStageCombinational((cur_inputbits).toInt))
      cur_output.vld := stage_penc.output.vld
      cur_output.idx := stage_penc.output.idx
      doBuild(base_offset, (cur_inputbits-1).toInt, stage_penc.input0)
      doBuild(base_offset+(inputbits/(pow(2,output_bits-cur_inputbits))).toInt, (cur_inputbits-1).toInt, stage_penc.input1)      


    } else {
      val base_penc = Module(new ParallelDec2PriorityEncoderBaseCombinational())
      cur_output.vld := base_penc.output.vld
      cur_output.idx := base_penc.output.idx
      base_penc.input0.vld := input.in(base_offset)
      base_penc.input1.vld := input.in(base_offset+1)
    }

  if (inputbits == 1) {
    // Base-case: valid = passthru, index = 0
    output.vld := input.in
    output.idx := 0.U
  } else {
    // General case: parallel priority encoder
    doBuild(0, output_bits-1, output)
  }
}