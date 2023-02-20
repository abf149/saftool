// See README.md for license details.



import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

/* Parallel priority encoder inter-stage interface encapsulation; idx = stage output index, vld = stage output valid */
class PriorityEncoderBundle(val bitwidth: Int) extends Bundle {
  val idx = UInt(bitwidth.W)
  val vld = UInt(1.W)
}

/* Priority encoder first stage - takes two "0-bit" inputs each with a valid signal, outputs 1-bit index with valid signal */
class ParallelDec2PriorityEncoderBaseCombinational() extends Module   with RequireSyncReset {
  val input0 = IO(new Bundle{val vld = UInt(1.W)})
  val input1 = IO(new Bundle{val vld = UInt(1.W)})
  val output = IO(new PriorityEncoderBundle(1))

  output.vld := (input0.vld.asBool || input1.vld.asBool).asUInt
  output.idx := input1.vld
}

/* Priority encoder intermediate stage - takes two n-bit inputs each with a valid signal, outputs n+1-bit index with valid signl */
class ParallelDec2PriorityEncoderStageCombinational(val bitwidth: Int) extends Module   with RequireSyncReset {
  val input0 = IO(new PriorityEncoderBundle(bitwidth))
  val input1 = IO(new PriorityEncoderBundle(bitwidth))
  val output = IO(new PriorityEncoderBundle(bitwidth+1))

  output.vld := (input0.vld.asBool || input1.vld.asBool).asUInt
  output.idx := Mux(input1.vld.asBool,Cat(input1.vld,input1.idx),Cat(input1.vld,input0.idx))
}

class ParallelDec2PriorityEncoderCombinational(val input_bits: Int) extends Module with RequireSyncReset {
  val output_bits = (log10(input_bits)/log10(2.0)).toInt

  val input = IO(new Bundle{val in = UInt(input_bits.W)})
  val output = IO(new PriorityEncoderBundle(output_bits))
  
  def doBuild(base_offset: Int, cur_input_bits: Int, cur_output: PriorityEncoderBundle): Unit =
    //val new_input_bits = (cur_input_bits/2).toInt 

    if (cur_input_bits > 0) {
      val stage_penc = Module(new ParallelDec2PriorityEncoderStageCombinational((cur_input_bits/2).toInt))
      cur_output.vld := stage_penc.output.vld
      cur_output.idx := stage_penc.output.idx
      doBuild(base_offset, (cur_input_bits/2).toInt, Flipped(stage_penc.input0))
      doBuild(base_offset+cur_input_bits, (cur_input_bits/2).toInt, Flipped(stage_penc.input1))      


    } else {
      val base_penc = Module(new ParallelDec2PriorityEncoderBaseCombinational())
      cur_output.vld := base_penc.output.vld
      cur_output.idx := base_penc.output.idx
      base_penc.input0.vld := input.in(base_offset)
      base_penc.input1.vld := input.in(base_offset+1)
    }

  doBuild(0, (input_bits/2).toInt , output)
}

/* Registered interface wrapped around combinatorial parallel priority encoder */
class ParallelDec2PriorityEncoderRegistered(val input_bits: Int) extends Module with RequireSyncReset {
  val output_bits = (log10(input_bits)/log10(2.0)).toInt

  val input = IO(new Bundle{val in = UInt(input_bits.W)})
  val output = IO(new PriorityEncoderBundle(output_bits))
  val input_reg = RegInit(0.U)
  val output_idx_reg = RegInit(0.U) 
  val output_vld_reg = RegInit(0.U)

  // Combinatorial unit
  val combinatorial_penc = Module(new ParallelDec2PriorityEncoderCombinational(input_bits))

  input_reg := input.in
  combinatorial_penc.input.in := input_reg
  output_idx_reg := combinatorial_penc.output.idx
  output_vld_reg := combinatorial_penc.output.vld 
  output.idx := output_idx_reg
  output.vld := output_vld_reg
}

/*
// Intersect unit {Format: C, metadata orchestration: uncoupled}
class IntersectFmtCDirBidirCombinational(metaDataWidth: Int) extends Module  with RequireSyncReset {
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

class IntersectFmtCDirLFCombinational(metaDataWidth: Int) extends Module {
  val io = IO(new Bundle {
    val inL = Input(UInt(metaDataWidth.W))
    //val in1_not_empty = Input(Bool())
    val inF = Input(UInt(metaDataWidth.W))
    val out_intersect = Output(UInt(metaDataWidth.W))
    val out_inF_request= Output(UInt(metaDataWidth.W))
  })

  // Registered outputs
  io.out_intersect := io.inL
  io.out_inF_request := io.inL
}


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
  val intersectCombinational = Module(new IntersectFmtCDirBidirCombinational(metaDataWidth))
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

*/