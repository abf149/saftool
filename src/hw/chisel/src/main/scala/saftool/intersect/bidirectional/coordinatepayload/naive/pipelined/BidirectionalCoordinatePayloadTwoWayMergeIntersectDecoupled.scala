package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

// Intersect unit {Format: C, direction: bidirectional}
class BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {

  val input0 = IO(Flipped(Decoupled(new PartialBidirectionalInputBundle(metaDataWidth))))
  val input1 = IO(Flipped(Decoupled(new PartialBidirectionalInputBundle(metaDataWidth))))
  val output = IO(Decoupled(new IntersectionOutputBundle(metaDataWidth)))

  // Data registers
  val in0_reg = RegInit(0.U)
  val in1_reg = RegInit(0.U)  
  val out_intersect_reg =   RegInit(0.U)
  val out_in1_gt_in0_reg = RegInit(false.B)
  val out_in1_eq_in0_reg = RegInit(true.B)
  
  // Handshaking registers
  val busy = RegInit(false.B)
  val out_valid = RegInit(false.B)  

  // Combinatorical intersection unit
  val intersectCombinational = Module(new IntersectFmtCDirBidirSingletonCombinational(metaDataWidth))
  intersectCombinational.reset := reset
  intersectCombinational.clock := clock
  intersectCombinational.io.in0 := in0_reg
  intersectCombinational.io.in1 := in1_reg 
  out_intersect_reg := intersectCombinational.io.out_intersect
  
  // Handshaking SM
  output.valid := out_valid
  input0.ready := (!busy) && (out_in1_eq_in0_reg || out_in1_gt_in0_reg)
  input1.ready := (!busy) && (out_in1_eq_in0_reg || (!out_in1_gt_in0_reg))  
  output.bits := DontCare

  when(busy) {

    out_intersect_reg := in0_reg //intersectCombinational.io.out_intersect
    output.bits.out := out_intersect_reg
    out_in1_eq_in0_reg := intersectCombinational.io.out_in1_eq_in0
    out_in1_gt_in0_reg := intersectCombinational.io.out_in1_gt_in0

    out_valid := true.B

    when(output.ready && out_valid) {
      busy := false.B
      out_valid := false.B
    }
  }.otherwise {
    when(out_in1_eq_in0_reg && input0.valid && input1.valid) {
      // in0 == in1: pop both input queues and compare new heads
      val bundle0 = input0.deq()
      val bundle1 = input1.deq()
      in0_reg := bundle0.in
      in1_reg := bundle1.in
      busy := true.B
    }.otherwise {
      when(out_in1_gt_in0_reg && input0.valid) {
        // in0 < in1: pop in0 and compare new in0 head to in1
        val bundle0 = input0.deq()
        in0_reg := bundle0.in
        busy := true.B
      }
      when((!out_in1_gt_in0_reg) && input1.valid) {
        // in1 < in0: pop in1 and compare in0 to new in1 head
        val bundle1 = input1.deq()
        in1_reg := bundle1.in
        busy := true.B      
      }
    }    
  }
}