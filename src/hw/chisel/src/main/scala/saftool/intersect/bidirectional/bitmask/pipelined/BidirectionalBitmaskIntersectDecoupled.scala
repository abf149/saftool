package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

// Intersect unit {Format: B, direction: bidirectional}
class BidirectionalBitmaskIntersectDecoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {

  val input0 = IO(Flipped(Decoupled(new PartialBidirectionalInputBundle(metaDataWidth))))
  val input1 = IO(Flipped(Decoupled(new PartialBidirectionalInputBundle(metaDataWidth))))
  val output = IO(Decoupled(new IntersectionOutputBundle(metaDataWidth)))

  // Data registers
  val in0_reg = RegInit(0.U)
  val in1_reg = RegInit(0.U)  
  val out_intersect_reg =   RegInit(0.U)
  
  // Handshaking registers
  val busy = RegInit(false.B)
  val out_valid = RegInit(false.B)  

  // Combinatorical intersection unit
  val intersectCombinational = Module(new IntersectFmtBDirBidirCombinational(metaDataWidth))
  intersectCombinational.reset := reset
  intersectCombinational.clock := clock
  intersectCombinational.io.in0 := in0_reg
  intersectCombinational.io.in1 := in1_reg 
  out_intersect_reg := intersectCombinational.io.out_intersect  
  
  // Handshaking SM
  output.valid := out_valid
  input0.ready := (!busy)
  input1.ready := (!busy)
  output.bits := DontCare

  when(busy) {

    output.bits.out := out_intersect_reg
    out_valid := true.B
    when(output.ready && out_valid) {
      busy := false.B
      out_valid := false.B
    }
  }.otherwise {
    when(input0.valid && input1.valid) {
      // in0 == in1: pop both input queues and compare new heads
      val bundle0 = input0.deq()
      val bundle1 = input1.deq()
      in0_reg := bundle0.in
      in1_reg := bundle1.in
      busy := true.B
    }  
  }
}