package saftool

import chisel3._
import chisel3.util._

class GeneralizedParallelKoggeStonePrefixSumRegistered(val vectorLength: Int, val inputBitWidth: Int) extends Module with RequireSyncReset {
  val outputWordBits = inputBitWidth + log2Ceil(vectorLength) + 1

  val input = IO(Input(Vec(vectorLength, UInt(inputBitWidth.W))))
  val output = IO(Output(Vec(vectorLength, UInt(outputWordBits.W))))

  // Registers for input and output
  val inputReg = RegInit(VecInit(Seq.fill(vectorLength)(0.U(inputBitWidth.W))))
  val outputReg = RegInit(VecInit(Seq.fill(vectorLength)(0.U(outputWordBits.W))))

  // Combinational unit
  val combinationalPrefixSum = Module(new GeneralizedParallelKoggeStonePrefixSumCombinational(vectorLength, inputBitWidth))

  // Connect input to the registered input
  inputReg := input

  // Connect registered input to the combinational unit
  combinationalPrefixSum.input := inputReg

  // Update the output register with the output of the combinational unit
  outputReg := combinationalPrefixSum.output

  // Connect the registered output to the module output
  output := outputReg
}
