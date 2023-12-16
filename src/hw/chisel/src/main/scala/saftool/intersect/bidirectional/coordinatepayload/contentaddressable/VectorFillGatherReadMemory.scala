package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class VectorFillGatherReadMemory(bitWidth: Int, numRegisters: Int, readPorts: Int) extends Module  with RequireSyncReset  {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val writeEnable = Input(Bool())
    val pingpongSelect = Input(Bool())
    val writeData = Input(Vec(numRegisters, UInt(bitWidth.W)))
    val readAddresses = Input(Vec(readPorts, UInt(log2Ceil(numRegisters).W)))
    val readEnable = Input(Bool())
    val readData = Output(Vec(readPorts, UInt(bitWidth.W)))
    val directRegisterOutputs = Output(Vec(numRegisters, UInt(bitWidth.W)))
  })

  val buffers = Reg(Vec(2, Vec(numRegisters, UInt(bitWidth.W))))
  val readBuffer = Wire(Vec(numRegisters, UInt(bitWidth.W)))

  // Logic for double-buffered write
  when(io.enable && io.writeEnable) {
    when(io.pingpongSelect) {
      buffers(1) := io.writeData
    } .otherwise {
      buffers(0) := io.writeData
    }
  }

  // Select buffer for read
  readBuffer := Mux(io.pingpongSelect, buffers(1), buffers(0))

  // Logic for gather read
  for (i <- 0 until readPorts) {
    io.readData(i) := Mux(io.enable && io.readEnable, readBuffer(io.readAddresses(i)), 0.U)
  }

  // Connect direct register outputs
  io.directRegisterOutputs := readBuffer
}

