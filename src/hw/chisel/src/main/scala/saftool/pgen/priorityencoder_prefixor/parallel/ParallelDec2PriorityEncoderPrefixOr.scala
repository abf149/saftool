package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class ParallelDec2PriorityEncoderBaseCombinationalPrioritizeLow() extends Module with RequireSyncReset {
  val input0 = IO(new Bundle{ val vld = Input(UInt(1.W)) })
  val input1 = IO(new Bundle{ val vld = Input(UInt(1.W)) })
  val output = IO(new PriorityEncoderBundle(1))

  // Convert UInt to Bool for logical operation
  output.vld := input0.vld.asBool() || input1.vld.asBool()
  // Convert UInt to Bool for Mux condition
  output.idx := Mux(input0.vld.asBool(), 0.U, 1.U)
}


class ParallelDec2PriorityEncoderStageCombinationalPrioritizeLow(val bitwidth: Int) extends Module with RequireSyncReset {
  val input0 = IO(Flipped(new PriorityEncoderBundle(bitwidth)))
  val input1 = IO(Flipped(new PriorityEncoderBundle(bitwidth)))
  val output = IO(new PriorityEncoderBundle(bitwidth+1))

  // Prioritize lower half index if valid, otherwise take upper half index
  output.vld := input0.vld.asBool() || input1.vld.asBool()
  output.idx := Mux(input0.vld.asBool(), Cat(0.U(1.W), input0.idx), Cat(1.U(1.W), input1.idx))
}

class ParallelDec2PriorityEncoderPrefixOr(val inputbits: Int) extends Module with RequireSyncReset {
  require(isPow2(inputbits), "Input length must be a power of 2")

  val io = IO(new Bundle {
    val in = Input(UInt(inputbits.W))
    val out = Output(new CombinedBundle(log2Ceil(inputbits), inputbits))
  })

  def buildCombined(input: UInt, idxWidth: Int, orWidth: Int): CombinedBundle = {
    val combinedOutput = Wire(new CombinedBundle(log2Ceil(inputbits), inputbits))

    // Check if all input bits are zero
    when(input === 0.U) {
      combinedOutput.priorityIdx := 0.U
      combinedOutput.prefixOrOut := 0.U
    } .otherwise {
      if (idxWidth == 0) {
        val baseEncoder = Module(new ParallelDec2PriorityEncoderBaseCombinationalPrioritizeLow())
        baseEncoder.input0.vld := input(0)
        baseEncoder.input1.vld := input(1)

        combinedOutput.priorityIdx := baseEncoder.output.idx
        combinedOutput.prefixOrOut := Mux(input(1), 
                                          Mux(input(0), "b01".U, "b11".U), 
                                          Cat(0.U(1.W), input(0)))
      } else {
        val stageEncoder = Module(new ParallelDec2PriorityEncoderStageCombinationalPrioritizeLow(idxWidth))
        val lowerHalf = buildCombined(input(orWidth/2-1, 0), idxWidth - 1, orWidth/2)
        val upperHalf = buildCombined(input(orWidth-1, orWidth/2), idxWidth - 1, orWidth/2)

        stageEncoder.input0.idx := lowerHalf.priorityIdx
        stageEncoder.input0.vld := lowerHalf.prefixOrOut(0)
        stageEncoder.input1.idx := upperHalf.priorityIdx
        stageEncoder.input1.vld := upperHalf.prefixOrOut(0)

        combinedOutput.priorityIdx := stageEncoder.output.idx
        val combinedUpperHalf = Mux(upperHalf.prefixOrOut.orR && lowerHalf.prefixOrOut.orR, 0.U((orWidth/2).W), upperHalf.prefixOrOut)
        val combinedLowerHalf = Mux(upperHalf.prefixOrOut.orR && !lowerHalf.prefixOrOut.orR, Fill(orWidth/2, "b1".U), lowerHalf.prefixOrOut)
        
        combinedOutput.prefixOrOut := (combinedUpperHalf << (orWidth/2)) | combinedLowerHalf
      }
    }

    combinedOutput.valid := input =/= 0.U
    combinedOutput
  }

  io.out := buildCombined(io.in, log2Ceil(inputbits) - 1, inputbits)
}