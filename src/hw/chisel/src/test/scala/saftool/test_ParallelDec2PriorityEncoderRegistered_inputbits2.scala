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

class Workload_ParallelDec2PriorityEncoderRegistered_Random(penc: ParallelDec2PriorityEncoderRegistered) extends PeekPokeTester(penc) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  //var j=0
  for (i <- 0 to 100)
  {
    poke(penc.input.in,rand.nextInt()) //85
    step(1)
  }
}

class Test_Sim_ParallelDec2PriorityEncoderRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "ParallelDec2PriorityEncoderRegistered"
  it should "inputbits2" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }    
  it should "inputbits4" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }    
  it should "inputbits8" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }        
  it should "inputbits16" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }  
  it should "inputbits32" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }  
  it should "inputbits64" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }
  it should "inputbits128" in {
    test(new ParallelDec2PriorityEncoderRegistered(inputbits = 128)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelDec2PriorityEncoderRegistered_Random(_))
  }               
}

class Test_Emit_ParallelDec2PriorityEncoderRegistered extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits2" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits2.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits4" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits4.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits8" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits8.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits16" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits16.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits32" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits32.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits64" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits64.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }  

  "Emit_ParallelDec2PriorityEncoderRegistered_inputbits128" in {
      var filename="ParallelDec2PriorityEncoderRegistered_inputbits128.v"
      var intersect=chisel3.getVerilogString(new ParallelDec2PriorityEncoderRegistered(inputbits = 128))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }    
}