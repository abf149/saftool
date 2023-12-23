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
    // Compute the minimum adder input/output bits required
    // # input bits = previous stage # output bits
    // # output bits = adderWidth
    val prevAdderWidth = inputBitWidth + log2Ceil(i+1) //log2Ceil(i * inputBitWidth) + 1    
    val adderWidth = inputBitWidth + log2Ceil(i + 1)
    // Truncate previous partial sum to the number of output bits of previous-stage
    // adder
    val widthMatch = Wire(UInt(prevAdderWidth.W))
    widthMatch := partialSums(i - 1)
    // Compute sum, using minimum number of required output bits
    val sum = Wire(UInt(adderWidth.W))
    sum := widthMatch + input(i)
    // Pad out the number of bits
    partialSums(i) := sum
  }

  output := partialSums
}