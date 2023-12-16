import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import java.nio.file.{Paths, Files}
import java.nio.charset.StandardCharsets

import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import java.nio.file.{Paths, Files}
import java.nio.charset.StandardCharsets

class Workload_ParallelDec2PriorityEncoderPrefixOr_Random(dut: ParallelDec2PriorityEncoderPrefixOr) extends PeekPokeTester(dut) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  for (i <- 0 to 100) {
    poke(dut.io.in, rand.nextInt(math.pow(2, dut.inputbits).toInt))
    step(1)
    // Add checks as necessary to validate output against expected behavior
  }
}

class Test_Sim_ParallelDec2PriorityEncoderPrefixOr extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "ParallelDec2PriorityEncoderPrefixOr"
  it should "inputbits32" in {
    test(new ParallelDec2PriorityEncoderPrefixOr(inputbits = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderPrefixOr_Random(_))
  }
  // ... Repeat for other input sizes
}

