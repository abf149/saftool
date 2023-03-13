// See README.md for license details.



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

class Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(intersect: BidirectionalCoordinatePayloadIntersectDecoupled) extends PeekPokeTester(intersect) {
  val rand = new scala.util.Random

  poke(intersect.input0.valid,0)  
  poke(intersect.input1.valid,0) 
  reset(2)
  step(3)
  expect(intersect.input0.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")
  expect(intersect.input1.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")  

  //var j=0
  for (i <- 0 to 10000)
  {
    while((peek(intersect.input0.ready)==0 && peek(intersect.input1.ready)==0)) 
    {
      
      step(1)
      //j+=1
    }

    if (peek(intersect.input0.ready)==1)
    {
      poke(intersect.input0.bits.in,rand.nextInt())
      poke(intersect.input0.valid,1)  
    }
    if (peek(intersect.input1.ready)==1)
    {
      poke(intersect.input1.bits.in,rand.nextInt())
      poke(intersect.input1.valid,1)     
    }
    step(1)
    poke(intersect.input0.valid,0)  
    poke(intersect.input1.valid,0)     
    poke(intersect.output.ready,1)    
    while (peek(intersect.output.valid) == 0) {
      step(1)
      //j+=1
    }    
    step(1)
    poke(intersect.output.ready,0) 
  }
}

class Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Default(intersect: BidirectionalCoordinatePayloadIntersectDecoupled) extends PeekPokeTester(intersect) {
  val rand = new scala.util.Random

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
  it should "metaDataWidth1" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 1)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }
  it should "metaDataWidth2" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }
  it should "metaDataWidth4" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }
  it should "metaDataWidth8" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }
  it should "metaDataWidth16" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }
  it should "metaDataWidth32" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }
  it should "metaDataWidth64" in {
    test(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalCoordinatePayloadIntersectDecoupled_Random(_))
  }            
}

class Test_Emit_BidirectionalCoordinatePayloadIntersectDecoupled extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth1" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth1.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 1))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth2" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth2.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth4" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth4.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

   "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth8" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth8.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth16" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth16.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth32" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth32.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }

  "Emit_BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth64" in {
      var filename="BidirectionalCoordinatePayloadIntersectDecoupled_metaDataWidth64.v"
      var intersect=chisel3.getVerilogString(new BidirectionalCoordinatePayloadIntersectDecoupled(metaDataWidth = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))
  }         

  /*
  "Emit_LeaderFollowerCoordinatePayloadIntersectDecoupled" in {  
      var filename="LeaderFollowerCoordinatePayloadIntersectDecoupled.v"

      x=chisel3.getVerilogString(new LeaderFollowerCoordinatePayloadFrontendDecoupled(metaDataWidth = 8))
      print(x)
      Files.write(Paths.get("src/verilog/pipeline_stage.v"), x.getBytes(StandardCharsets.UTF_8))        
      */

      /*
      x=chisel3.getVerilogString(new LeaderFollowerCoordinatePayloadIntersectDecoupled(metaDataWidth = 8))
      print(x)
      Files.write(Paths.get("src/verilog/IntersectFmtCDirLFDecoupled.v"), x.getBytes(StandardCharsets.UTF_8))

  }
  */

}