package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

// Fully combinational Ripple prefix sum
class BitmaskRipplePrefixSumCombinational(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))

  val partial_sums = Wire(Vec(bitwidth, UInt(output_wordbits.W)))

  partial_sums(0) := input.bitmask(0)
  for (i <- 1 until bitwidth) {
    val prev_adder_width = log2Ceil(i) + 1    
    val adder_width = log2Ceil(i + 1) + 1
    val width_match = Wire(UInt(prev_adder_width.W))
    width_match := partial_sums(i - 1)
    val width_match_reg = RegInit(0.U(prev_adder_width.W))
    width_match_reg := width_match
    val sum = Wire(UInt(adder_width.W))
    sum := width_match_reg + input.bitmask(i) //+&
    partial_sums(i) := sum.zext.asUInt
  }

  output.sums := partial_sums
}