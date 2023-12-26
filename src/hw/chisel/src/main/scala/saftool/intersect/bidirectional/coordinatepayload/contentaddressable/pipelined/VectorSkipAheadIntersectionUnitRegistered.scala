package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class VectorSkipAheadIntersectionUnitRegistered(val vectorLength: Int, val numTags: Int, val tagBitWidth: Int) extends Module with RequireSyncReset {
  val io = IO(new Bundle {
    // Mirrored interfaces for Left and Right (Input)
    val left_disableComparatorMask = Input(UInt(numTags.W))
    val right_disableComparatorMask = Input(UInt(numTags.W))
    val left_head_in = Input(UInt(log2Ceil(numTags).W))
    val right_head_in = Input(UInt(log2Ceil(numTags).W))
    // Mirrored interfaces for Left and Right (Output)
    val left_disableNextStageMask = Output(UInt(numTags.W))
    val right_disableNextStageMask = Output(UInt(numTags.W))
    val left_head_out = Output(UInt(log2Ceil(numTags).W))
    val right_head_out = Output(UInt(log2Ceil(numTags).W))
    val left_is_empty = Output(Bool())
    val right_is_empty = Output(Bool())
    // General control interfaces (Input)
    val enable = Input(Bool())
    val skip_from_in = Input(Bool())
    // General control interfaces (Output)
    val skip_from_out = Output(Bool())
    val pingpongSelect = Input(Bool())
    // Match interfaces (Output)
    val is_match = Output(Bool())
    val match_tag = Output(UInt(tagBitWidth.W))
    val num_matches = Output(UInt(log2Ceil(vectorLength + 1).W))    

    val readData = Output(Vec(vectorLength, UInt(tagBitWidth.W)))

    val left_writeEnable = Input(Bool())
    val right_writeEnable = Input(Bool())
    val left_writeData = Input(Vec(numTags, UInt(tagBitWidth.W)))
    val right_writeData = Input(Vec(numTags, UInt(tagBitWidth.W)))
    val readEnable = Input(Bool())
  })

  val core = Module(new VectorSkipAheadIntersectionUnit(vectorLength, numTags, tagBitWidth))

  // Input Registers
  val left_disableComparatorMask_reg = RegNext(io.left_disableComparatorMask)
  val right_disableComparatorMask_reg = RegNext(io.right_disableComparatorMask)
  val left_head_in_reg = RegNext(io.left_head_in)
  val right_head_in_reg = RegNext(io.right_head_in)
  val enable_reg = RegNext(io.enable)
  val skip_from_in_reg = RegNext(io.skip_from_in)
  val pingpongSelect_reg = RegNext(io.pingpongSelect)
  val left_writeEnable_reg = RegNext(io.left_writeEnable)
  val right_writeEnable_reg = RegNext(io.right_writeEnable)
  val left_writeData_reg = Reg(Vec(numTags, UInt(tagBitWidth.W)))
  val right_writeData_reg = Reg(Vec(numTags, UInt(tagBitWidth.W)))
  val readEnable_reg = RegNext(io.readEnable)

  // Connect the registered inputs to the core component
  core.io.left_disableComparatorMask := left_disableComparatorMask_reg
  core.io.right_disableComparatorMask := right_disableComparatorMask_reg
  core.io.left_head_in := left_head_in_reg
  core.io.right_head_in := right_head_in_reg
  core.io.enable := enable_reg
  core.io.skip_from_in := skip_from_in_reg
  core.io.pingpongSelect := pingpongSelect_reg
  core.io.left_writeEnable := left_writeEnable_reg
  core.io.right_writeEnable := right_writeEnable_reg
  for(i <- 0 until numTags) {
    left_writeData_reg(i) := RegNext(io.left_writeData(i))
    right_writeData_reg(i) := RegNext(io.right_writeData(i))
  }
  core.io.left_writeData := left_writeData_reg
  core.io.right_writeData := right_writeData_reg
  core.io.readEnable := readEnable_reg

  // Output Registers
  val left_disableNextStageMask_reg = RegNext(core.io.left_disableNextStageMask)
  val right_disableNextStageMask_reg = RegNext(core.io.right_disableNextStageMask)
  val left_head_out_reg = RegNext(core.io.left_head_out)
  val right_head_out_reg = RegNext(core.io.right_head_out)
  val left_is_empty_reg = RegNext(core.io.left_is_empty)
  val right_is_empty_reg = RegNext(core.io.right_is_empty)
  val skip_from_out_reg = RegNext(core.io.skip_from_out)
  val is_match_reg = RegNext(core.io.is_match)
  val match_tag_reg = RegNext(core.io.match_tag)
  val num_matches_reg = RegNext(core.io.num_matches)
  // Output Register for readData
  val readData_reg = Reg(Vec(vectorLength, UInt(tagBitWidth.W)))
  for(i <- 0 until vectorLength) {
    readData_reg(i) := RegNext(core.io.readData(i))
  }

  // Connect the registered outputs to the IO
  io.readData := readData_reg

  // Connect the registered outputs to the IO
  io.left_disableNextStageMask := left_disableNextStageMask_reg
  io.right_disableNextStageMask := right_disableNextStageMask_reg
  io.left_head_out := left_head_out_reg
  io.right_head_out := right_head_out_reg
  io.left_is_empty := left_is_empty_reg
  io.right_is_empty := right_is_empty_reg
  io.skip_from_out := skip_from_out_reg
  io.is_match := is_match_reg
  io.match_tag := match_tag_reg
  io.num_matches := num_matches_reg
}
