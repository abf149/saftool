package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class RegisteredEqualityComparator(bitwidth: Int) extends Module  with RequireSyncReset {
  val io = IO(new Bundle {
    val inL = Input(UInt(bitwidth.W))
    val inR = Input(UInt(bitwidth.W))
    val out = Output(Bool())
  })

  // Registered inputs
  val inL_reg = RegInit(0.U) // TODO: DontCare
  val inR_reg = RegInit(0.U)    

  // Registered outputs
  val out_reg = RegInit(0.U)

  inL_reg := io.inL
  inR_reg := io.inR
  out_reg := inL_reg === inR_reg
  io.out := out_reg
}