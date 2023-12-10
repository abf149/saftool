package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Parallel prefix sum wrapper input interface encapsulation*/
class ParallelPrefixSumWrapperInputBundle(val bitwidth: Int) extends Bundle {
  val bitmask = Input(UInt(bitwidth.W))
}

/* Parallel prefix sum wrapper output interface encapsulation*/
class ParallelPrefixSumWrapperOutputBundle(val bitwidth: Int, val num_items: Int) extends Bundle {
  val sums = Output(Vec(num_items,UInt(bitwidth.W)))
}