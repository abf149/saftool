// See README.md for license details.

package saftool

import chisel3._
import chisel3.util.Decoupled

// Intersect unit {Format: C, metadata orchestration: uncoupled}
class AUX_Intersect_Format_C_MDOrch_Uncoupled(metaDataWidth: Int) extends Module  with RequireSyncReset {
  val io = IO(new Bundle {
    val in0 = Input(UInt(metaDataWidth.W))
    val in1 = Input(UInt(metaDataWidth.W))
    val out_intersect = Output(UInt(metaDataWidth.W))
    val out_in1_geq_in0 = Output(Bool())
    val out_in1_eq_in0 = Output(Bool())
  })

  // Registers
  val in0_reg = RegInit(0.U)
  val in1_reg = RegInit(0.U)  
  val out_intersect_reg =   RegInit(0.U)
  val out_in1_geq_in0_reg = RegInit(false.B)
  val out_in1_eq_in0_reg = RegInit(false.B)
  
  // Registered inputs
  in0_reg := io.in0
  in1_reg := io.in1  

  // Compare coordinate metadata
  out_in1_geq_in0_reg := (in1_reg >= in0_reg)
  out_in1_eq_in0_reg := (in1_reg === in0_reg)

  out_intersect_reg := in0_reg

  // Registered outputs
  io.out_intersect := out_intersect_reg
  io.out_in1_geq_in0 := out_in1_geq_in0_reg
  io.out_in1_eq_in0 := out_in1_eq_in0_reg  
}

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