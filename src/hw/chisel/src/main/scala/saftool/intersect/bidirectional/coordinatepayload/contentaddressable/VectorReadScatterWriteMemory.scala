package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class VectorReadScatterWriteMemory(val bitWidth: Int, val numRegisters: Int, val writePorts: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    val enable = Input(Bool())
    val readEnable = Input(Bool())
    val pingpongSelect = Input(Bool())
    val readData = Output(Vec(numRegisters, UInt(bitWidth.W)))
    val writeAddresses = Input(Vec(writePorts, UInt(log2Ceil(numRegisters).W)))
    val writeEnable = Input(Vec(writePorts, Bool()))
    val writeData = Input(Vec(writePorts, UInt(bitWidth.W)))
  })

  val buffers = Reg(Vec(2, Vec(numRegisters, UInt(bitWidth.W))))
  val writeBuffer = Wire(Vec(numRegisters, UInt(bitWidth.W)))

  // Logic for double-buffered read
  when(io.enable && io.readEnable) {
    writeBuffer := Mux(io.pingpongSelect, buffers(0), buffers(1))
  }.otherwise {
    writeBuffer := VecInit(Seq.fill(numRegisters)(0.U(bitWidth.W)))
  }

  // Logic for scatter write
  for (i <- 0 until writePorts) {
    when(io.enable && io.writeEnable(i)) {
      val bufferIndex = Mux(!io.pingpongSelect, 1.U, 0.U) // Inverted selection for write
      buffers(bufferIndex)(io.writeAddresses(i)) := io.writeData(i)
    }
  }

  // Connect read data output
  io.readData := writeBuffer
}
