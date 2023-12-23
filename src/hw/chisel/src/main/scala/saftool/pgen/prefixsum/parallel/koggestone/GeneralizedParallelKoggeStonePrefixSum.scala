package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class GeneralizedParallelKoggeStonePrefixSumCombinational(val vectorLength: Int, val inputBitWidth: Int) extends Module with RequireSyncReset {
  val outputWordBits = inputBitWidth + log2Ceil(vectorLength) + 1

  val input = IO(Input(Vec(vectorLength, UInt(inputBitWidth.W))))
  val output = IO(Output(Vec(vectorLength, UInt(outputWordBits.W))))

  // Build one level of Kogge-Stone parallel prefix-sum
  def doBuild(currentLevel: Array[UInt], numElements: Int, lvlIdx: Int): Array[UInt] = {
    val lvlStride = pow(2, lvlIdx).toInt
    val bitsOut = inputBitWidth + log2Ceil(numElements) + 1 // Corrected bit width calculation
    val newLevel = new Array[UInt](numElements)

    for (jdx <- 0 until lvlStride) {
      newLevel(jdx) = Wire(UInt(bitsOut.W))
      newLevel(jdx) := currentLevel(jdx)
    }

    for (jdx <- lvlStride until numElements) {
      newLevel(jdx) = Wire(UInt(bitsOut.W))
      newLevel(jdx) := (currentLevel(jdx).pad(bitsOut) + currentLevel(jdx - lvlStride).pad(bitsOut))
    }

    newLevel
  }

  val numLvls = log2Ceil(vectorLength) + 1 // Adjusted for the depth of Kogge-Stone tree
  var logicLvls: Array[Array[UInt]] = Array.ofDim[UInt](numLvls, vectorLength)

  logicLvls(0) = input.toArray

  // Build successive Kogge-Stone layers
  for (idx <- 1 until numLvls) {
    logicLvls(idx) = doBuild(logicLvls(idx - 1), vectorLength, idx - 1)
  }

  // Wire Kogge-Stone final layer to output
  for (idx <- 0 until vectorLength) {
    output(idx) := logicLvls(numLvls - 1)(idx)
  }
}

