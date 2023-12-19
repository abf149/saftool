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

class IntersectionIO(val numTags: Int, val tagBitWidth: Int) extends Bundle {
  val disableComparatorMask = Input(UInt(numTags.W))
  val tagMemoryInterface = Input(Vec(numTags, UInt(tagBitWidth.W)))
  val memReadTag = Input(UInt(tagBitWidth.W))
  val head_in = Input(UInt(log2Ceil(numTags).W))
  val memoryLookupAddress = Output(UInt(log2Ceil(numTags).W))
  val memoryLookupEnable = Output(Bool())
  val disableNextStageMask = Output(UInt(numTags.W))
  val head_out = Output(UInt(log2Ceil(numTags).W))
  val is_empty = Output(Bool())
}
