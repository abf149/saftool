// See README.md for license details.

package saftool

import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

/* "Efficient Processing" sparse representation format enum */
sealed trait SparseFormat
case object C extends SparseFormat
case object B extends SparseFormat

/* Ready/valid handshaking interface primitives */
class PartialBidirectionalInputBundle(val bitwidth: Int) extends Bundle {

  val in = UInt(bitwidth.W)
}

class IntersectionOutputBundle(val bitwidth: Int) extends Bundle {
  val out = UInt(bitwidth.W)
}

class IntersectFmtBDirBidirCombinational(mdTileSize: Int) extends Module   with RequireSyncReset {
  val io = IO(new Bundle {
    val in0 = Input(UInt(mdTileSize.W))
    val in1 = Input(UInt(mdTileSize.W))
    val out_intersect = Output(UInt(mdTileSize.W))
  })

  // Combinational bidirectional bitmask intersection
  io.out_intersect := io.in0 & io.in1
}

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

class RegisteredAdder(bitwidth: Int) extends Module {
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

/* Leader/follower intersection pipeline components */

/*
object LeaderFollowerState {
  object FrontendState extends ChiselEnum {
    val sNotBusy, sFwdBusy, sMemFBusy, sFwdMemFBusy = Value
  }
  object BackendState extends ChiselEnum {
    val sNotBusy, sBusy, sStall = Value
  }  
}

// Frontend
// - inL: leader metadata input
// - outF: leader metadata output to facilitate (downstream) follower memory lookup
// - outFwd: registered metadata output
class LeaderFollowerCoordinatePayloadFrontendDecoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {
  import LeaderFollowerState._

  val inL = IO(Flipped(Decoupled(new Bundle{val in = Input(UInt(metaDataWidth.W))})))
  val outF = IO(Decoupled(new Bundle{val out = Input(UInt(metaDataWidth.W))}))
  val outFwd = IO(Decoupled(new Bundle{val out = Input(UInt(metaDataWidth.W))}))

  // Data registers
  val inL_reg = RegInit(0.U)
  val outFwd_reg = RegInit(0.U)  

  // SM register
  val state =   RegInit(FrontendState.sNotBusy)
  
  // Handshaking registers
  val out_valid_memf = RegInit(false.B)  
  val out_valid_fwd = RegInit(false.B)  

  // Handshaking SM
  outFwd.valid := out_valid_fwd
  outF.valid := out_valid_memf

  inL.ready := (state === FrontendState.sNotBusy)
  outF.bits.out := inL_reg
  outFwd_reg := inL_reg
  outFwd.bits := DontCare

  switch (state) {
    // State machine for managing follower memory (memF) memory requests & forwarding
    is (FrontendState.sNotBusy) {
      when(inL.valid) {
        val bundle = inL.deq()
        inL_reg := bundle.in
        state := FrontendState.sFwdMemFBusy
      }
    }
    is (FrontendState.sFwdBusy) {
      outFwd.bits.out := outFwd_reg
      out_valid_fwd := true.B    
      when(outFwd.ready) {
        state := FrontendState.sNotBusy
        out_valid_fwd := false.B
      }      
    }
    is (FrontendState.sMemFBusy) {
      out_valid_memf := true.B
      when(outF.ready) {
        state := FrontendState.sNotBusy
        out_valid_memf := false.B
      }
    }
    is (FrontendState.sFwdMemFBusy) {
      outFwd.bits.out := outFwd_reg
      out_valid_memf := true.B
      out_valid_fwd := true.B      
      when(outF.ready && outFwd.ready) {
        state := FrontendState.sNotBusy
        out_valid_memf := false.B
        out_valid_fwd := false.B 
      }.elsewhen(outF.ready) {
        state := FrontendState.sFwdBusy
        out_valid_memf := false.B
      }.elsewhen(outFwd.ready) {
        state := FrontendState.sMemFBusy
        out_valid_fwd := false.B 
      }
    }
  }
}

*/

/*

// E2E
// - inL: leader metadata input
// - outF: leader metadata output to facilitate (downstream) follower memory lookup
// - inF:
// - out_intersect:
class LeaderFollowerCoordinatePayloadDecoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {
  import LeaderFollowerState._

  val inL = IO(Flipped(Decoupled(new Bundle{val in = Input(UInt(metaDataWidth.W))})))
  val outF = IO(Decoupled(new Bundle{val out = Input(UInt(metaDataWidth.W))}))
  val inF = IO(Flipped(Decoupled(new Bundle{val in = Input(UInt(metaDataWidth.W))})))
  val out_intersect = IO(Decoupled(new Bundle{val out = Input(UInt(metaDataWidth.W))}))

  // Data registers
  val inL_reg = RegInit(0.U)
  //val inF_reg = RegInit(0.U)  
  val out_intersect_reg = RegInit(0.U)  
  //val inFwd_reg = RegInit(0.U)    

  // SM register
  val state =   RegInit(BackendState.sNotBusy)
  
  // Handshaking registers
  val out_valid = RegInit(false.B)  

  // Frontend subcomponent
  // - frontend.outFwd will be used later
  val frontend = Module(new LeaderFollowerCoordinatePayloadFrontendDecoupled(metaDataWidth))
  frontend.inL <> inL
  frontend.outF <> outF
  
  // val sNotBusy, sBusy, sStall = Value

  // Handshaking SM
  out_intersect.valid := out_valid
  inL.ready := (state === BackendState.sNotBusy)
  //inFwd_reg := frontend.outFwd.bits.out
  //val inFwd_valid = frontend.outFwd.valid
  //val inFwd_ready = frontend.outFwd.ready
  out_intersect.bits := DontCare

  switch (state) {
    is (BackendState.sNotBusy) {
      when(inL.valid) {
        val bundle = inL.deq()
        inL_reg := bundle.in
        state := BackendState.sFwdMemFBusy
      }
    }
    is (BackendState.sFwdBusy) {
      outFwd.bits.out := outFwd_reg
      out_valid_fwd := true.B    
      when(outFwd.ready) {
        state := BackendState.sNotBusy
        out_valid_fwd := false.B
      }      
    }
    is (BackendState.sMemFBusy) {
      out_valid_memf := true.B
      when(outF.ready) {
        state := BackendState.sNotBusy
        out_valid_memf := false.B
      }
    }
    is (BackendState.sFwdMemFBusy) {
      outFwd.bits.out := outFwd_reg
      out_valid_memf := true.B
      out_valid_fwd := true.B      
      when(outF.ready && outFwd.ready) {
        state := BackendState.sNotBusy
        out_valid_memf := false.B
        out_valid_fwd := false.B 
      }.elsewhen(outF.ready) {
        state := BackendState.sFwdBusy
        out_valid_memf := false.B
      }.elsewhen(outFwd.ready) {
        state := BackendState.sMemFBusy
        out_valid_fwd := false.B 
      }
    }
  }
}

*/

/*

// Intersect unit {Format: B, direction: bidirectional}
class LeaderFollowerCoordinatePayloadIntersectDecoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {

  val inputL = IO(Flipped(Decoupled(new PartialBidirectionalInputBundle(metaDataWidth))))
  val inputF = IO(Flipped(Decoupled(new PartialBidirectionalInputBundle(metaDataWidth))))
  val output = IO(Decoupled(new IntersectionOutputBundle(metaDataWidth)))
  val output_inF_request = IO(Decoupled(new IntersectionOutputBundle(metaDataWidth)))

  // Data registers
  val inL_reg = RegInit(0.U)
  val inF_reg = RegInit(0.U)  
  val out_intersect_reg =   RegInit(0.U)
  
  // Handshaking registers
  val busy = RegInit(false.B)
  val out_valid = RegInit(false.B)  

  // Combinatorical intersection unit
  val intersectCombinational = Module(new IntersectFmtCDirLFCombinational(metaDataWidth))
  intersectCombinational.reset := reset
  intersectCombinational.clock := clock
  intersectCombinational.io.inL := inL_reg
  intersectCombinational.io.inF := inF_reg 
  
  // Handshaking SM
  output.valid := out_valid
  inputL.ready := (!busy)
  input1.ready := (!busy)
  output.bits := DontCare

  when(busy) {

    output.bits.out := intersectCombinational.io.out_intersect
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

/*

class AUX_Intersect_Format_B_MDOrch_Uncoupled(mdTileSize: Int) extends Module   with RequireSyncReset {
  val io = IO(new Bundle {
    val in0 = Input(UInt(mdTileSize.W))
    val in1 = Input(UInt(mdTileSize.W))
    val out = Output(UInt(mdTileSize.W))
  })

  // Registers
  val in0_reg = RegInit(0.U)
  val in1_reg = RegInit(0.U)  
  val out_reg = RegInit(0.U)

  // Registered inputs
  in0_reg := io.in0
  in1_reg := io.in1

  // Simple bitwise-AND  
  out_reg := in0_reg & in1_reg

  // Registered output
  io.out := out_reg
}

class AUX_Intersect_Format_C_MDOrch_Coupled(metaDataWidth: Int) extends Module {
  val io = IO(new Bundle {
    val in0 = Input(UInt(metaDataWidth.W))
    val in1_not_empty = Input(Bool())
    val in1 = Input(UInt(metaDataWidth.W))
    val out_intersect = Output(UInt(metaDataWidth.W))
    val out_vld = Output(Bool())
    val in1_request= Output(UInt(metaDataWidth.W))
  })

  // Registers
  val in0_reg = RegInit(0.U)
  val in1_reg = RegInit(0.U)  
  val in1_not_empty_reg = RegInit(false.B)
  val out_intersect_reg = RegInit(0.U)  
  val out_vld_reg = RegInit(false.B)
  val in1_request_reg = RegInit(false.B)

  // Registered inputs
  in0_reg := io.in0
  in1_reg := io.in1
  in1_not_empty_reg := io.in1_not_empty

  // Leader/follower logic
  out_intersect_reg := in0_reg
  out_vld_reg := in1_not_empty_reg
  in1_request_reg := in1_not_empty_reg

  // Registered outputs
  io.out_intersect := out_intersect_reg
  io.out_vld := out_vld_reg
  io.in1_request := in1_request_reg
}

*/