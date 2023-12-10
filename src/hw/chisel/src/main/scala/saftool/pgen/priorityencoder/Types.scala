package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Parallel priority encoder inter-stage interface encapsulation; idx = stage output index, vld = stage output valid */
class PriorityEncoderBundle(val bitwidth: Int) extends Bundle {
  val idx = Output(UInt(bitwidth.W))
  val vld = Output(UInt(1.W))
}