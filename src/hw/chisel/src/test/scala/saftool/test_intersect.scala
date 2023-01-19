// See README.md for license details.

package saftool

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

class Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Default(intersect: BidirectionalCoordinatePayloadIntersectDecoupled) extends PeekPokeTester(intersect) {
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

class Workload_BidirectionalBitmaskIntersectDecoupled_Default(intersect: BidirectionalBitmaskIntersectDecoupled) extends PeekPokeTester(intersect) {
  poke(intersect.input0.valid,0)  
  poke(intersect.input1.valid,0) 
  reset(2)
  step(3)
  expect(intersect.input0.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")
  expect(intersect.input1.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")  
  poke(intersect.input0.bits.in,Integer.parseInt("01010101", 2)) //85
  poke(intersect.input0.valid,1)  
  poke(intersect.input1.bits.in,Integer.parseInt("11001101", 2)) //205
  poke(intersect.input1.valid,1)     
  step(1)
  poke(intersect.input0.valid,0)  
  poke(intersect.input1.valid,0)     
  poke(intersect.output.ready,1)

  while (peek(intersect.output.valid) == 0) {
    step(1)
  }

  poke(intersect.output.ready,0) // Expect Integer.parseInt("01000101", 2)) // 69
}

class Test_Sim_BidirectionalCoordinatePayloadIntersectDecoupled extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "BidirectionalCoordinatePayloadIntersectDecoupled"
  it should "default_workload" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Default(_))
  }

  behavior of "BidirectionalBitmaskIntersectDecoupled"
  it should "default_workload" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Default(_))
  }  
}

class Test_Emit_Intersection extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled" in {
      var filename="BidirectionalBitmaskIntersectDecoupled.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }


  "Emit_LeaderFollowerCoordinatePayloadIntersectDecoupled" in {  
      var filename="LeaderFollowerCoordinatePayloadIntersectDecoupled.v"
      /*
      x=chisel3.getVerilogString(new LeaderFollowerCoordinatePayloadFrontendDecoupled(metaDataWidth = 8))
      print(x)
      Files.write(Paths.get("src/verilog/pipeline_stage.v"), x.getBytes(StandardCharsets.UTF_8))        
      */

      /*
      x=chisel3.getVerilogString(new LeaderFollowerCoordinatePayloadIntersectDecoupled(metaDataWidth = 8))
      print(x)
      Files.write(Paths.get("src/verilog/IntersectFmtCDirLFDecoupled.v"), x.getBytes(StandardCharsets.UTF_8))
      */
  }
}