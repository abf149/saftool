package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

// Brent-Kung parallel prefix sum
class BrentKungParallelPrefixSumCombinational(val bitwidth: Int) extends Module with RequireSyncReset {
  val output_wordbits = (log10(bitwidth) / log10(2.0)).toInt + 1

  val input = IO(new ParallelPrefixSumWrapperInputBundle(bitwidth))
  val output = IO(new ParallelPrefixSumWrapperOutputBundle(output_wordbits, bitwidth))

  def doUpSweep(current_level: Array[UInt], num_elements: Int, lvl_idx: Int): Array[UInt] = {
    val new_level = new Array[UInt](num_elements)
    val lvl_stride = pow(2, lvl_idx).toInt

    for (jdx <- 0 until num_elements) {
      new_level(jdx) = Wire(UInt((lvl_idx + 2).W))
      if (jdx % lvl_stride == 0 && jdx + lvl_stride < num_elements) {
        new_level(jdx) := current_level(jdx) + current_level(jdx + lvl_stride)
      } else {
        new_level(jdx) := current_level(jdx)
      }
    }

    return new_level
  }

  def doDownSweep(current_level: Array[UInt], num_elements: Int, lvl_idx: Int): Array[UInt] = {
    val new_level = new Array[UInt](num_elements)
    val lvl_stride = pow(2, lvl_idx).toInt

    for (jdx <- 0 until num_elements) {
      new_level(jdx) = Wire(UInt((output_wordbits).W))
    }

    for (jdx <- 0 until num_elements) {
      //new_level(jdx) = Wire(UInt((output_wordbits).W))
      if (jdx % lvl_stride == 0 && jdx + lvl_stride < num_elements) {
        new_level(jdx) := current_level(jdx + lvl_stride)
        new_level(jdx + lvl_stride) := current_level(jdx) + current_level(jdx + lvl_stride)
      } else if (jdx % lvl_stride != 0) {
        new_level(jdx) := current_level(jdx)
      }
    }

    return new_level
  }

  val num_lvls = output_wordbits - 1
  var up_sweep_levels: Array[Array[UInt]] = new Array[Array[UInt]](num_lvls)
  var down_sweep_levels: Array[Array[UInt]] = new Array[Array[UInt]](num_lvls)

  up_sweep_levels(0) = new Array[UInt](bitwidth)
  for (kdx <- 0 until bitwidth) {
    up_sweep_levels(0)(kdx) = Wire(UInt(1.W))
    up_sweep_levels(0)(kdx) := input.bitmask(kdx)
  }

  for (idx <- 1 until num_lvls) {
    up_sweep_levels(idx) = doUpSweep(up_sweep_levels(idx - 1), bitwidth, idx - 1)
  }

  down_sweep_levels(num_lvls - 1) = Array.fill(bitwidth)(Wire(UInt(output_wordbits.W)))
  down_sweep_levels(num_lvls - 1)(0) := 0.U
  for (idx <- 1 until bitwidth) {
    down_sweep_levels(num_lvls - 1)(idx) := up_sweep_levels(num_lvls - 1)(idx)
  }

  for (idx <- num_lvls - 2 to 0 by -1) {
    down_sweep_levels(idx) = doDownSweep(down_sweep_levels(idx + 1), bitwidth, idx)
  }

  for (idx <- 0 until bitwidth) {
    output.sums(idx) := down_sweep_levels(0)(idx)
  }
}