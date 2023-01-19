// See README.md for license details.

package saftool

import chisel3._
import chiseltest._
import org.scalatest.freespec.AnyFreeSpec
import chisel3.experimental.BundleLiterals._

import java.io.{ByteArrayOutputStream, File, PrintStream}

import chisel3._
import chisel3.stage.ChiselOutputFileAnnotation
import chiseltest._
import chiseltest.experimental.sanitizeFileName
import firrtl.options.OutputAnnotationFileAnnotation
import firrtl.stage.OutputFileAnnotation
import treadle.{VerboseAnnotation, WriteVcdAnnotation}
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

import java.nio.file.{Paths, Files}
import java.nio.charset.StandardCharsets

import chisel3.stage.ChiselStage
import chisel3.Input
import chisel3.util._
//import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import chisel3._
import chiseltest._
import chiseltest.iotesters._
import org.scalatest.freespec.AnyFreeSpec
import chisel3.experimental.BundleLiterals._

import saftool._

class Help_Test_Do_Intersection(intersect: BidirectionalCoordinatePayloadIntersectDecoupled) extends PeekPokeTester(intersect) {
  poke(intersect.input0.valid,0)  
  poke(intersect.input1.valid,0) 
  reset(2)
  step(3)
  expect(intersect.input0.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")
  expect(intersect.input1.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")  
  poke(intersect.input0.bits.in,1)
  poke(intersect.input0.valid,1)  
  poke(intersect.input1.bits.in,1)  
  poke(intersect.input1.valid,1)     
  step(1)
  poke(intersect.input0.valid,0)  
  poke(intersect.input1.valid,0)     
  poke(intersect.output.ready,1)

  while (peek(intersect.output.valid) == 0) {
    step(1)
  }

  poke(intersect.output.ready,0)
}

class Test_Sim_BidirectionalCoordinatePayloadIntersectDecoupled extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "BidirectionalCoordinatePayloadIntersectDecoupled"

  it should "default_workload" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Help_Test_Do_Intersection(_))
  }
}

/*
class Test_Do_Intersection extends AnyFreeSpec with ChiselScalatestTester {


  "Test_Emit_Intersection" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(8)) { dut =>
          

          dut.input0.initSource()
          dut.input0.setSourceClock(dut.clock)
          dut.input1.initSource()
          dut.input1.setSourceClock(dut.clock)      
          dut.output.initSink()
          dut.output.setSinkClock(dut.clock)

          val in0_0=(new PartialBidirectionalInputBundle(8)).Lit(_.in -> 1.U)
          val in1_0=(new PartialBidirectionalInputBundle(8)).Lit(_.in -> 1.U)
          val out_0=(new IntersectionOutputBundle(8)).Lit(_.out -> 1.U)      

          dut.input0.enq(in0_0)

          /*
          fork {
            //dut.input0.enq(in0_0)
            //dut.input1.enq(in1_0)
            dut.clock.step(10)
          }.fork{
            dut.clock.step(10)
            dut.output.expectDequeue(out_0)
          }.join()
          */
    }

    val testDir = new File("test_run_dir" +
      File.separator +
      sanitizeFileName(s"Intersection should output matching coordinates"))

    //val vcdFileOpt = testDir.listFiles.find { f =>
    //  f.getPath.endsWith(".vcd")
    //}

  }
}
*/

/*
class OptionsPassingTest extends AnyFlatSpec with ChiselScalatestTester {
  
  "Intersection" in {
      //try {
        test(

            Module(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth=8))
        ).withAnnotations(Seq(WriteVcdAnnotation)) { dut =>

          
          dut.input0.initSource()
          dut.input0.setSourceClock(dut.clock)
          dut.input1.initSource()
          dut.input1.setSourceClock(dut.clock)      
          dut.output.initSink()
          dut.output.setSinkClock(dut.clock)

          val in0_0=(new PartialBidirectionalInputBundle(8)).Lit(_.in -> 1.U)
          val in1_0=(new PartialBidirectionalInputBundle(8)).Lit(_.in -> 1.U)
          val out_0=(new IntersectionOutputBundle(8)).Lit(_.out -> 1.U)      

          dut.input0.enq(in0_0)

          /*
          fork {
            //dut.input0.enq(in0_0)
            //dut.input1.enq(in1_0)
            dut.clock.step(10)
          }.fork{
            dut.clock.step(10)
            dut.output.expectDequeue(out_0)
          }.join()
          */
          
        }
    //} catch { case e: Throwable => print(e.getStackTrace.mkString("\n")) }
    val testDir = new File("test_run_dir" +
      File.separator +
      sanitizeFileName(s"Intersection should output matching coordinates"))

    //val vcdFileOpt = testDir.listFiles.find { f =>
    //  f.getPath.endsWith(".vcd")
    //}

    //vcdFileOpt.isDefined should be(true)
  }

  /*
  it should "allow turning on verbose mode" in {
    val outputStream = new ByteArrayOutputStream()
    Console.withOut(new PrintStream(outputStream)) {
      test(new Module {}).withAnnotations(Seq(VerboseAnnotation)) { c =>
        c.clock.step(1)
      }
    }

    val output = outputStream.toString

    output.contains("Symbol table:") should be(true)
    output.contains("clock/prev") should be(true)
  }
  */
}
*/


/*
class GCDSpec2 extends AnyFreeSpec with ChiselScalatestTester with VerilatorBackendAnnotation {

  "Gcd should calculate proper greatest common denominator (2)" in {
    test(new DecoupledGcd(16)) { dut =>
      dut.input.initSource()
      dut.input.setSourceClock(dut.clock)
      dut.output.initSink()
      dut.output.setSinkClock(dut.clock)

      val testValues = for { x <- 0 to 10; y <- 0 to 10} yield (x, y)
      val inputSeq = testValues.map { case (x, y) => (new GcdInputBundle(16)).Lit(_.value1 -> x.U, _.value2 -> y.U) }
      val resultSeq = testValues.map { case (x, y) =>
        (new GcdOutputBundle(16)).Lit(_.value1 -> x.U, _.value2 -> y.U, _.gcd -> BigInt(x).gcd(BigInt(y)).U)
      }

      fork {
        // push inputs into the calculator, stall for 11 cycles one third of the way
        val (seq1, seq2) = inputSeq.splitAt(resultSeq.length / 3)
        dut.input.enqueueSeq(seq1)
        dut.clock.step(11)
        dut.input.enqueueSeq(seq2)
      }.fork {
        // retrieve computations from the calculator, stall for 10 cycles one half of the way
        val (seq1, seq2) = resultSeq.splitAt(resultSeq.length / 2)
        dut.output.expectDequeueSeq(seq1)
        dut.clock.step(10)
        dut.output.expectDequeueSeq(seq2)
      }.join()

    }
  }
}
*/