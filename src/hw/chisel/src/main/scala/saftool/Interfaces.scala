package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

class ReadMuxInterface(val arraySize: Int, val wordWidth: Int) extends Bundle {
    val enable = Input(Bool())
    val controlSignal = Input(UInt(log2Ceil(arraySize).W))
    val selectedWire = Output(UInt(wordWidth.W))
}

class WriteMuxInterface(val arraySize: Int, val wordWidth: Int) extends Bundle {
    val enable = Input(Bool())
    val writeAddress = Input(UInt(log2Ceil(arraySize).W))
    val writeData = Input(UInt(wordWidth.W))
}

class VectorizedDynamicReadMux(arraySize: Int, wordWidth: Int) extends Module {
    val io = IO(new Bundle {
        val readMuxVec = Vec(arraySize, new ReadMuxInterface(arraySize, wordWidth))
        val sharedWireArray = Input(Vec(arraySize, UInt(wordWidth.W)))
    })

    // Default value for selectedWire
    val defaultValue = 0.U(wordWidth.W)

    // Implement the multiplexer logic for each instance
    for (i <- 0 until arraySize) {
        when(io.readMuxVec(i).arraySize.U === 1.U) { // Corrected comparison to use UInt
            // Passthrough case for arraySize == 1
            io.readMuxVec(i).selectedWire := Mux(io.readMuxVec(i).enable, io.sharedWireArray(0), defaultValue)
        } .elsewhen(io.readMuxVec(i).enable) {
            // Multiplexer logic for arraySize > 1
            io.readMuxVec(i).selectedWire := MuxLookup(io.readMuxVec(i).controlSignal, defaultValue, 
                                                    io.sharedWireArray.zipWithIndex.map{ case (wire, idx) => (idx.U -> wire) })
        } .otherwise {
            io.readMuxVec(i).selectedWire := defaultValue
        }
    }
}

class VectorizedDynamicWriteMux(arraySize: Int, wordWidth: Int) extends Module {
    val io = IO(new Bundle {
        val dynamicWriteMuxVec = Vec(arraySize, new WriteMuxInterface(arraySize, wordWidth))
        val sharedWriteArray = Output(Vec(arraySize, UInt(wordWidth.W)))
    })

    // Initialize the sharedWriteArray to zeros
    io.sharedWriteArray.foreach(_ := 0.U)

    // Logic for each write instance
    for (i <- 0 until arraySize) {
        when(io.dynamicWriteMuxVec(i).enable) {
            io.sharedWriteArray(io.dynamicWriteMuxVec(i).writeAddress) := io.dynamicWriteMuxVec(i).writeData
        }
    }
}