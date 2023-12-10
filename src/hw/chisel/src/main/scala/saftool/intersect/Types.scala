package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

/* Ready/valid handshaking interface primitives */
class PartialBidirectionalInputBundle(val bitwidth: Int) extends Bundle {
  val in = UInt(bitwidth.W)
}

class IntersectionOutputBundle(val bitwidth: Int) extends Bundle {
  val out = UInt(bitwidth.W)
}