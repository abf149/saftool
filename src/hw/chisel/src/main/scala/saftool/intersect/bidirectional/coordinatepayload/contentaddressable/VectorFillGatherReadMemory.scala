package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class VectorFillGatherReadMemory(val bitWidth: Int, val numRegisters: Int, val readPorts: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val writeEnable = Input(Bool())
    val pingpongSelect = Input(Bool())
    val writeData = Input(Vec(numRegisters, UInt(bitWidth.W)))
    val readAddresses = Input(Vec(readPorts, UInt(log2Ceil(numRegisters).W)))
    val readEnable = Input(Vec(readPorts, Bool())) // Changed to Vec of Bool
    val readData = Output(Vec(readPorts, UInt(bitWidth.W)))
    val directRegisterOutputs = Output(Vec(numRegisters, UInt(bitWidth.W)))
  })

  val buffers = Reg(Vec(2, Vec(numRegisters, UInt(bitWidth.W))))
  val readBuffer = Wire(Vec(numRegisters, UInt(bitWidth.W)))

  // Logic for double-buffered write
  when(io.enable && io.writeEnable) {
    when(io.pingpongSelect) {
      buffers(0) := io.writeData
    } .otherwise {
      buffers(1) := io.writeData
    }
  }

  // Select buffer for read
  readBuffer := Mux(io.pingpongSelect, buffers(1), buffers(0))

  // Updated Logic for gather read
  for (i <- 0 until readPorts) {
    io.readData(i) := Mux(io.enable && io.readEnable(i), readBuffer(io.readAddresses(i)), 0.U)
  }

  // Connect direct register outputs
  io.directRegisterOutputs := readBuffer
}

/* 
package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class VectorFillGatherReadMemory(val bitWidth: Int, val numRegisters: Int, val readPorts: Int) extends Module with RequireSyncReset {
  require(readPorts > 0, "There must be at least one read port")

  val io = IO(new Bundle {
    val enable = Input(Bool())
    val writeEnable = Input(Bool())
    val pingpongSelect = Input(Bool())
    val writeData = Input(Vec(numRegisters, UInt(bitWidth.W)))
    val readAddresses = Input(Vec(readPorts, UInt(log2Ceil(numRegisters).W)))
    val readEnable = Input(Vec(readPorts, Bool()))
    val readData = Output(Vec(readPorts, UInt(bitWidth.W)))
    val directRegisterOutputs = Output(Vec(readPorts, Vec(numRegisters, UInt(bitWidth.W))))
  })

  // Each sub-buffer contains 'readPorts' vectors, each having 'numRegisters' registers
  val buffers = Reg(Vec(2, Vec(readPorts, Vec(numRegisters, UInt(bitWidth.W)))))

  // Logic for double-buffered write
  when(io.enable && io.writeEnable) {
    val bufferIndex = Mux(io.pingpongSelect, 0.U, 1.U)
    for (i <- 0 until readPorts) {
      buffers(bufferIndex)(i) := io.writeData
    }
  }

  // Logic for reading from the buffer
  val selectedBuffer = Mux(io.pingpongSelect, buffers(1), buffers(0))
  for (i <- 0 until readPorts) {
    io.readData(i) := Mux(io.enable && io.readEnable(i), selectedBuffer(i)(io.readAddresses(i)), 0.U)
  }

  // Providing access to the register vectors of the selected sub-buffer
  for (i <- 0 until readPorts) {
    io.directRegisterOutputs(i) := selectedBuffer(i)
  }
}



/* 
/*
class VectorFillGatherReadMemory(val bitWidth: Int, val numRegisters: Int, val readPorts: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val writeEnable = Input(Bool())
    val pingpongSelect = Input(Bool())
    val writeData = Input(Vec(numRegisters, UInt(bitWidth.W)))
    val readAddresses = Input(Vec(readPorts, UInt(log2Ceil(numRegisters).W)))
    val readEnable = Input(Vec(readPorts, Bool()))
    val readData = Output(Vec(readPorts, UInt(bitWidth.W)))
    val directRegisterOutputs = Output(Vec(numRegisters, UInt(bitWidth.W)))
  })

  val buffers = Reg(Vec(2, Vec(numRegisters, UInt(bitWidth.W))))
  val readBuffer = Wire(Vec(numRegisters, UInt(bitWidth.W)))

  // Logic for double-buffered write
  when(io.enable && io.writeEnable) {
    when(io.pingpongSelect) {
      buffers(0) := io.writeData
    } .otherwise {
      buffers(1) := io.writeData
    }
  }

  // Select buffer for read
  readBuffer := Mux(io.pingpongSelect, buffers(1), buffers(0))

  // Implement read logic using multiplexers
  for (i <- 0 until readPorts) {
    val readAddressMux = MuxLookup(io.readAddresses(i), 0.U, readBuffer.zipWithIndex.map { case (data, idx) => (idx.U, data) })
    io.readData(i) := Mux(io.enable && io.readEnable(i), readAddressMux, 0.U)
  }

  // Connect direct register outputs using multiplexers
  for (i <- 0 until numRegisters) {
    val directOutputMux = MuxLookup(i.U, 0.U, readBuffer.zipWithIndex.map { case (data, idx) => (idx.U, data) })
    io.directRegisterOutputs(i) := directOutputMux
  }
}
*/
*/
*/