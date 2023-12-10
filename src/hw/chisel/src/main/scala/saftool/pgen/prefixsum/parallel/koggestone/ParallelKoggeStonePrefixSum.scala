package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Combinational Kogge-Stone parallel prefix sum */
class ParallelKoggeStonePrefixSumCombinational(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth)/log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits,bitwidth))

  // Build one level of Kogge-Stone parallel prefix-sum
  def doBuild(current_level: Array[UInt], num_elements: Int, lvl_idx: Int): Array[UInt] = {
    val lvl_stride = pow(2,lvl_idx).toInt
    val bits_in = lvl_idx+1
    val bits_out = lvl_idx+2
    val new_level = new Array[UInt](num_elements)

    for (jdx <- 0 until lvl_stride) {
      new_level(jdx) = Wire(UInt(bits_out.W))
      new_level(jdx) := current_level(jdx).zext.asUInt
    }

    for (jdx <- lvl_stride until num_elements) { 
      new_level(jdx) = Wire(UInt(bits_out.W))
      new_level(jdx) := current_level(jdx).zext.asUInt + current_level(jdx - lvl_stride).zext.asUInt
    }

    return new_level
  }

  val num_lvls = output_wordbits
  var logic_lvls:Array[Array[UInt]] = new Array[Array[UInt]](num_lvls)

  logic_lvls(0) = new Array[UInt](bitwidth)    
  for (kdx <- 0 until bitwidth) {
    logic_lvls(0)(kdx) = Wire(UInt(1.W))
    logic_lvls(0)(kdx) := input.bitmask(kdx)
  }

  // Build successive Kogge-Stone layers
  for (idx <- 1 until num_lvls) {
    logic_lvls(idx) = doBuild(logic_lvls(idx-1), bitwidth, idx-1)
  }

  // Wire Kogge-Stone final layer to output

  for (idx <- 0 until bitwidth) {
    output.sums(idx) := logic_lvls(num_lvls-1)(idx)
  }
}