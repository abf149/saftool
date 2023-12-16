package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

// Intersect unit {Format: C, metadata orchestration: uncoupled}

class CheckIfFinished(headWidth: Int, N: UInt) extends Module {
  val io = IO(new Bundle {
    // Enable signal
    val enable = Input(Bool())

    // Input head indices
    val new_in0_head = Input(UInt(headWidth.W))
    val new_in1_head = Input(UInt(headWidth.W))

    // Output Boolean signal
    val isFinished = Output(Bool())
  })

  // Logic to check if either head index equals N
  when(io.enable) {
    io.isFinished := (io.new_in0_head === N) || (io.new_in1_head === N)
  } .otherwise {
    io.isFinished := false.B
  }
}


class OperandPopDecider(headWidth: Int) extends Module {
  val io = IO(new Bundle {
    // Enable signal
    val enable = Input(Bool())

    // Existing inputs
    val in_in1_gt_in0 = Input(Bool())
    val in_in1_eq_in0 = Input(Bool())
    val in0_head = Input(UInt(headWidth.W))
    val in1_head = Input(UInt(headWidth.W))
    val out_head = Input(UInt(headWidth.W))

    // Updated outputs
    val new_in0_head = Output(UInt((headWidth).W))
    val new_in1_head = Output(UInt((headWidth).W))
    val new_out_head = Output(UInt((headWidth).W))
  })

  // Conditional logic based on the enable signal
  when(io.enable) {
    io.new_in0_head := io.in0_head + (io.in_in1_gt_in0 || io.in_in1_eq_in0).asUInt
    io.new_in1_head := io.in1_head + (io.in_in1_eq_in0 || !io.in_in1_gt_in0).asUInt
    io.new_out_head := io.out_head + io.in_in1_eq_in0.asUInt
  } .otherwise {
    // When not enabled, keep the current values
    io.new_in0_head := io.in0_head
    io.new_in1_head := io.in1_head
    io.new_out_head := io.out_head
  }
}

class IntersectFmtCDirBidirStageCombinational(headWidth: Int, metaDataWidth: Int, arraySize: Int) extends Module {
  val io = IO(new Bundle {
    val enable_in = Input(Bool())
    val enable_out = Output(Bool())
    val in0_head = Input(UInt(headWidth.W))
    val in1_head = Input(UInt(headWidth.W))
    val out_head = Input(UInt(headWidth.W))
    val new_in0_head = Output(UInt(headWidth.W))
    val new_in1_head = Output(UInt(headWidth.W))
    val new_out_head = Output(UInt(headWidth.W))

    // Read and Write Mux Interfaces
    val readMux0 = new ReadMuxInterface(arraySize, metaDataWidth)
    val readMux1 = new ReadMuxInterface(arraySize, metaDataWidth)
    val writeMux = new WriteMuxInterface(arraySize, metaDataWidth)
  })

  // Instance of IntersectFmtCDirBidirSingletonCombinational
  val intersectUnit = Module(new IntersectFmtCDirBidirSingletonCombinational(metaDataWidth))
  intersectUnit.io.in0 := io.readMux0.selectedWire
  intersectUnit.io.in1 := io.readMux1.selectedWire
  intersectUnit.io.out_intersect := io.writeMux.writeData // Assuming this connection is correct

  // Configure Read Mux Interfaces
  io.readMux0.controlSignal := io.in0_head
  io.readMux1.controlSignal := io.in1_head
  io.readMux0.enable := io.enable_in
  io.readMux1.enable := io.enable_in

  // Configure Write Mux Interface
  io.writeMux.writeData := intersectUnit.io.out_intersect
  io.writeMux.enable := intersectUnit.io.out_in1_eq_in0 && io.enable_in
  io.writeMux.writeAddress := io.out_head

  // OperandPopDecider instance
  val operandPopDecider = Module(new OperandPopDecider(headWidth))
  operandPopDecider.io.enable := io.enable_in
  operandPopDecider.io.in_in1_gt_in0 := intersectUnit.io.out_in1_gt_in0
  operandPopDecider.io.in_in1_eq_in0 := intersectUnit.io.out_in1_eq_in0
  operandPopDecider.io.in0_head := io.in0_head
  operandPopDecider.io.in1_head := io.in1_head
  operandPopDecider.io.out_head := io.out_head
  io.new_in0_head := operandPopDecider.io.new_in0_head
  io.new_in1_head := operandPopDecider.io.new_in1_head
  io.new_out_head := operandPopDecider.io.new_out_head

  // CheckIfFinished instance
  val checkIfFinished = Module(new CheckIfFinished(headWidth, (2*arraySize - 1).U)) // Assuming N = arraySize - 1
  checkIfFinished.io.enable := io.enable_in
  checkIfFinished.io.new_in0_head := io.new_in0_head
  checkIfFinished.io.new_in1_head := io.new_in1_head
  io.enable_out := !checkIfFinished.io.isFinished && io.enable_in
}

class WholePipeline(metaDataWidth: Int, arraySize: Int) extends Module {
  val M = 2 * arraySize - 1
  val headWidth = log2Ceil(arraySize) // Assuming headWidth based on arraySize

  val io = IO(new Bundle {
    val enable_in = Input(Bool())
    val enable_out = Output(Bool())
    val inputWireArrays = Input(Vec(M, Vec(2, Vec(arraySize, UInt(metaDataWidth.W)))))
    val outputWireArrays = Output(Vec(M, Vec(arraySize, UInt(metaDataWidth.W))))
    val outputFlagArrays = Output(Vec(M, Vec(arraySize, UInt(1.W))))
  })

  // Create instances of pipeline stages, read muxes, and write muxes
  val pipelineStages = Seq.fill(M)(Module(new IntersectFmtCDirBidirStageCombinational(headWidth, metaDataWidth, arraySize)))
  val readMuxes = Seq.fill(M)(Module(new VectorizedDynamicReadMux(arraySize, metaDataWidth)))
  val writeMuxesData = Seq.fill(M)(Module(new VectorizedDynamicWriteMux(arraySize, metaDataWidth)))
  val writeMuxesFlag = Seq.fill(M)(Module(new VectorizedDynamicWriteMux(arraySize, 1)))

  // Initial head inputs and enable signal for the first stage
  pipelineStages.head.io.in0_head := 0.U
  pipelineStages.head.io.in1_head := 0.U
  pipelineStages.head.io.out_head := 0.U
  pipelineStages.head.io.enable_in := io.enable_in

  // Wire stages, read muxes, and write muxes
  for(i <- 0 until M) {
    // Connect read muxes to input wire arrays
    readMuxes(i).io.sharedWireArray := io.inputWireArrays(i)

    // Connect pipeline stage to read muxes
    pipelineStages(i).io.readMux0 <> readMuxes(i).io.readMuxVec(0)
    pipelineStages(i).io.readMux1 <> readMuxes(i).io.readMuxVec(1)

    // Connect pipeline stage to write muxes
    pipelineStages(i).io.writeMux <> writeMuxesData(i).io.dynamicWriteMuxVec
    writeMuxesData(i).io.sharedWriteArray := io.outputWireArrays(i)

    // Special handling for write mux flags
    writeMuxesFlag(i).io.sharedWriteArray := io.outputFlagArrays(i)
    writeMuxesFlag(i).io.dynamicWriteMuxVec.foreach { w =>
      w.enable := pipelineStages(i).io.writeMux.enable
      w.writeData := pipelineStages(i).io.writeMux.enable
      w.writeAddress := pipelineStages(i).io.writeMux.writeAddress
    }

    // Chain stages
    if (i < M - 1) {
      pipelineStages(i + 1).io.in0_head := pipelineStages(i).io.new_in0_head
      pipelineStages(i + 1).io.in1_head := pipelineStages(i).io.new_in1_head
      pipelineStages(i + 1).io.out_head := pipelineStages(i).io.new_out_head
      pipelineStages(i + 1).io.enable_in := pipelineStages(i).io.enable_out
    }
  }

  // Set enable_out for the last stage
  io.enable_out := pipelineStages.last.io.enable_out
}