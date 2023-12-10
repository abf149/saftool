package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class IntersectFmtBDirBidirCombinational(mdTileSize: Int) extends Module   with RequireSyncReset {
  val io = IO(new Bundle {
    val in0 = Input(UInt(mdTileSize.W))
    val in1 = Input(UInt(mdTileSize.W))
    val out_intersect = Output(UInt(mdTileSize.W))
  })

  // Combinational bidirectional bitmask intersection
  io.out_intersect := io.in0 & io.in1
}// Intersect unit {Format: B, direction: bidirectional}