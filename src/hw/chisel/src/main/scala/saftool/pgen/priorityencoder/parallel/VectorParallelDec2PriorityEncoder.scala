package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class VectorParallelDec2PriorityEncoder(val vectorLength: Int, val inputbits: Int) extends Module {
  val outputBits = log2Ceil(inputbits)
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val input = Input(UInt(inputbits.W))
    val outputs = Output(Vec(vectorLength, UInt(outputBits.W)))
    val bitmask_next = Output(UInt(inputbits.W))
    val num_valid = Output(UInt((outputBits+1).W))
    val is_done = Output(Bool())
  })

  val encoders = Seq.fill(vectorLength)(Module(new ParallelDec2PriorityEncoderCombinational(inputbits)))
  
  // Defaults
  val is_done_internal = Wire(Vec(vectorLength, Bool()))
  //is_done_internal(0) := false.B
  io.is_done := false.B
  io.bitmask_next := 0.U
  io.num_valid := 0.U
  for (i <- encoders.indices) {
    encoders(i).input.in := 0.U //maskedInputs(i)
    io.outputs(i) := 0.U
    is_done_internal(i) := false.B
  }

  // Enabled case
  when(io.enable){
    val maskedInputs = Wire(Vec(vectorLength+1, UInt(inputbits.W)))
    maskedInputs(0) := io.input
    for (i <- encoders.indices) {
        if (i > 0) {
            is_done_internal(i) := is_done_internal(i-1)
            when(encoders(i - 1).output.vld =/= 0.U){ // Fixed type mismatch
                maskedInputs(i) := maskedInputs(i - 1) & ~UIntToOH(encoders(i - 1).output.idx, inputbits)
            }.otherwise{
                if (i == 1) {
                    // If 0th encoder returned valid low there are no 1s in the input
                    io.num_valid := 0.U
                    is_done_internal(0) := true.B
                } else {
                    when(!is_done_internal(i-2)) {
                        // num_valid is the index of the first encoder which returned valid low
                        io.num_valid := (i-1).U
                        is_done_internal(i-1) := true.B
                    }
                }
                maskedInputs(i) :=  0.U
            }
        }
        encoders(i).input.in := maskedInputs(i)
        io.outputs(i) := encoders(i).output.idx
    }

    //is_done_internal(vectorLength) := is_done_internal(vectorLength-1)
    when(encoders(vectorLength - 1).output.vld =/= 0.U){ // Fixed type mismatch
        maskedInputs(vectorLength) := maskedInputs(vectorLength - 1) & ~UIntToOH(encoders(vectorLength - 1).output.idx, inputbits)
        // If we have gotten this far without an encoder returning valid low, then
        // the number of 1s in the input is >= the number of combinational encoder stages,
        // and thus we found only the first vectorLength 1s
        io.num_valid := vectorLength.U
        // Note that if the number of 1s is exactly vectorLength, then maskedInputs(vectorLength) will be 0.U
        // which will drive is_done high
        is_done_internal(vectorLength-1) := maskedInputs(vectorLength) === 0.U
    }.otherwise{
        if (vectorLength == 1) {
            // If the only encoder returned valid low there are no 1s in the input in the first place
            io.num_valid := 0.U
            is_done_internal(0) := true.B
        } else {
            when(!is_done_internal(vectorLength-2)) {
                // num_valid is the index of the first encoder which returned valid low
                io.num_valid := (vectorLength-1).U
                is_done_internal(vectorLength-1) := true.B
            }
        }
        maskedInputs(vectorLength) :=  0.U
    }

    io.bitmask_next := maskedInputs(vectorLength)
    io.is_done := is_done_internal(vectorLength-1)
  }
}
