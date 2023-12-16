package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

// Intersect unit {Format: C, metadata orchestration: uncoupled}
class IntersectFmtCDirBidirSingletonCombinational(metaDataWidth: Int) extends Module  with RequireSyncReset {
  val io = IO(new Bundle {
    val in0 = Input(UInt(metaDataWidth.W))
    val in1 = Input(UInt(metaDataWidth.W))
    val out_intersect = Output(UInt(metaDataWidth.W))
    val out_in1_gt_in0 = Output(Bool())
    val out_in1_eq_in0 = Output(Bool())
  })

  // Combinational naive bidirectional coordinate intersection:
  // compare coordinate metadata
  io.out_in1_gt_in0 := (io.in1 > io.in0)
  io.out_in1_eq_in0 := (io.in1 === io.in0)
  io.out_intersect := io.in0
}