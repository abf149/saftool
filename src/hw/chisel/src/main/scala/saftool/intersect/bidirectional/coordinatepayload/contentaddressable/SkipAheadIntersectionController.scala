package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}
import scala.math._

class SkipAheadIntersectionController(val numTags: Int, val tagBitWidth: Int) extends Module with RequireSyncReset {
  require(isPow2(numTags), "Number of tags must be a power of 2")

  val io = IO(new Bundle {
    // Existing interfaces
    val enable = Input(Bool())
    val skip_from_in = Input(Bool())
    val skip_from_out = Output(Bool())
    val is_match = Output(Bool())
    val match_tag = Output(UInt(tagBitWidth.W))
    val left = new IntersectionIO(numTags, tagBitWidth)
    val right = new IntersectionIO(numTags, tagBitWidth)

    // Additional interfaces for tag and trigger inputs
    //val tagInput = Input(UInt(tagBitWidth.W))
    //val triggerInput = Input(Bool())
  })

  val leftController = Module(new HalfAssociativeIntersectionController(numTags, tagBitWidth))
  val rightController = Module(new HalfAssociativeIntersectionController(numTags, tagBitWidth))

  // Wiring for existing interfaces
  leftController.io.enable := io.enable
  rightController.io.enable := io.enable

  Seq((io.left, leftController.io), (io.right, rightController.io)).foreach { case (extIO, intIO) =>
    // Existing wiring
    intIO.disableComparatorMask := extIO.disableComparatorMask
    intIO.tagMemoryInterface := extIO.tagMemoryInterface
    intIO.memReadTag := extIO.memReadTag
    intIO.head_in := extIO.head_in
    extIO.memoryLookupAddress := intIO.memoryLookupAddress
    extIO.memoryLookupEnable := intIO.memoryLookupEnable
    extIO.disableNextStageMask := intIO.disableNextStageMask
    extIO.head_out := intIO.head_out
    extIO.is_empty := intIO.is_empty

    // Wiring for tagInput and triggerInput
    //intIO.tagInput := io.tagInput
    //intIO.triggerInput := io.triggerInput
    intIO.triggerInput := true.B
  }

  // Default initializations
  io.skip_from_out := false.B
  io.is_match := false.B
  io.match_tag := 0.U
  io.left.head_out := 0.U
  io.right.head_out := 0.U

  leftController.io.force_peek := false.B
  rightController.io.force_peek := false.B


  when(io.enable) {
    leftController.io.force_peek := !io.skip_from_in
    rightController.io.force_peek := io.skip_from_in

    rightController.io.tagInput := leftController.io.peek_out
    leftController.io.tagInput := rightController.io.peek_out

    val are_equal = leftController.io.peek_out === rightController.io.peek_out

    io.left.head_out := Mux(io.skip_from_in && are_equal, leftController.io.head_out + 1.U, leftController.io.head_out)
    io.right.head_out := Mux(!io.skip_from_in && are_equal, rightController.io.head_out + 1.U, rightController.io.head_out)

    io.is_match := leftController.io.isMatch && rightController.io.isMatch && are_equal
    io.match_tag := Mux(are_equal, leftController.io.peek_out, 0.U)

    io.skip_from_out := !io.skip_from_in
  }.otherwise {
    leftController.io.force_peek := false.B
    rightController.io.force_peek := false.B

    io.skip_from_out := false.B
    io.is_match := false.B
    io.match_tag := 0.U
    io.left.head_out := 0.U
    io.right.head_out := 0.U
  }
}
