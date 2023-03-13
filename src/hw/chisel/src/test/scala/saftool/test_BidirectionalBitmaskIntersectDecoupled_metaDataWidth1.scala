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

class Workload_BidirectionalBitmaskIntersectDecoupled_Random(intersect: BidirectionalBitmaskIntersectDecoupled) extends PeekPokeTester(intersect) {
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
    while((peek(intersect.input0.ready)==0 || peek(intersect.input1.ready)==0)) 
    {
      
      step(1)
      //j+=1
    }
    poke(intersect.input0.bits.in,rand.nextInt()) //85
    poke(intersect.input0.valid,1)  
    poke(intersect.input1.bits.in,rand.nextInt()) //205
    poke(intersect.input1.valid,1)     
    step(1)
    poke(intersect.input0.valid,0)  
    poke(intersect.input1.valid,0)     
    poke(intersect.output.ready,1)    
    while (peek(intersect.output.valid) == 0) {
      step(1)
      //j+=1
    }    
    step(1)
    poke(intersect.output.ready,0) // Expect Integer.parseInt("01000101", 2)) // 69
  }
}

class Workload_BidirectionalBitmaskIntersectDecoupled_Default(intersect: BidirectionalBitmaskIntersectDecoupled) extends PeekPokeTester(intersect) {
  poke(intersect.input0.valid,0)  
  poke(intersect.input1.valid,0) 
  reset(2)
  step(3)
  expect(intersect.input0.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")
  expect(intersect.input1.ready, 1, s"intersect.input0.ready expected: 1, got: ${peek(intersect.input0.ready)}")  
  poke(intersect.input0.bits.in,Integer.parseInt("01010101", 10)) //85
  poke(intersect.input0.valid,1)  
  poke(intersect.input1.bits.in,Integer.parseInt("11001101", 10)) //205
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

class Test_Sim_BidirectionalBitmaskIntersectDecoupled extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "BidirectionalBitmaskIntersectDecoupled"
  it should "metaDataWidth1" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 1)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }  
  it should "metaDataWidth2" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }  
  it should "metaDataWidth4" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }  
  it should "metaDataWidth8" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }  
  it should "metaDataWidth16" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }  
  it should "metaDataWidth32" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }  
  it should "metaDataWidth64" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }      
  it should "metaDataWidth128" in {
    test(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 128)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BidirectionalBitmaskIntersectDecoupled_Random(_))
  }                
}

class Test_Emit_BidirectionalBitmaskIntersectDecoupled extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth1" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth1.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 1))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth2" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth2.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth4" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth4.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth8" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth8.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth16" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth16.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth32" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth32.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth64" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth64.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }            

  "Emit_BidirectionalBitmaskIntersectDecoupled_metaDataWidth128" in {
      var filename="BidirectionalBitmaskIntersectDecoupled_metaDataWidth128.v"
      var intersect=chisel3.getVerilogString(new BidirectionalBitmaskIntersectDecoupled(metaDataWidth = 128))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }              
}