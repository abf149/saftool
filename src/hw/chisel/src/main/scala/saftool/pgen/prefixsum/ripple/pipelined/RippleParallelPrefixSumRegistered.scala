package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

// Registered interface wrapped around the Ripple parallel prefix sum
class RippleParallelPrefixSumRegistered(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))
  val bitmask_reg = RegInit(0.U(bitwidth.W))
  val output_wordbits_reg = RegInit(VecInit(Seq.fill(bitwidth)(0.U(output_wordbits.W))))

  // Combinational unit
  val combinational_prefix_sum = Module(new RippleParallelPrefixSumCombinational(bitwidth))

  bitmask_reg := input.bitmask
  combinational_prefix_sum.input.bitmask := bitmask_reg
  output_wordbits_reg := combinational_prefix_sum.output.sums
  output.sums := output_wordbits_reg
}