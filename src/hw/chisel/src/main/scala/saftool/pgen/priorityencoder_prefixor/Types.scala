package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class CombinedBundle(val idxWidth: Int, val orWidth: Int) extends Bundle {
  val priorityIdx = UInt(idxWidth.W)
  val prefixOrOut = UInt(orWidth.W)
}