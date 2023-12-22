package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class GeneralizedRipplePrefixSumCombinational(val vectorLength: Int, val inputBitWidth: Int) extends Module with RequireSyncReset {
  val outputWordBits = inputBitWidth + log2Ceil(vectorLength) + 1

  val input = IO(Input(Vec(vectorLength, UInt(inputBitWidth.W))))
  val output = IO(Output(Vec(vectorLength, UInt(outputWordBits.W))))

  val partialSums = Wire(Vec(vectorLength, UInt(outputWordBits.W)))

  partialSums(0) := input(0)
  for (i <- 1 until vectorLength) {
    val prevAdderWidth = log2Ceil(i * inputBitWidth) + 1    
    val adderWidth = log2Ceil((i + 1) * inputBitWidth) + 1
    val widthMatch = Wire(UInt(prevAdderWidth.W))
    widthMatch := partialSums(i - 1)
    val widthMatchReg = RegInit(0.U(prevAdderWidth.W))
    widthMatchReg := widthMatch
    val sum = Wire(UInt(adderWidth.W))
    sum := widthMatchReg + input(i)
    partialSums(i) := sum
  }

  output := partialSums
}