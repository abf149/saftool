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

class Workload_ParallelKoggeStonePrefixSumRegistered_Random(pfsum: ParallelKoggeStonePrefixSumRegistered) extends PeekPokeTester(pfsum) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  //var j=0
  for (i <- 0 to 100)
  {
    poke(pfsum.input.bitmask,rand.nextInt()) //85
    step(1)
  }
}

class Test_Sim_ParallelKoggeStonePrefixSumRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "ParallelKoggeStonePrefixSumRegistered"
  it should "bitwidth2" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }    
  it should "bitwidth4" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }    
  it should "bitwidth8" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }        
  it should "bitwidth16" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }  
  it should "bitwidth32" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }  
  it should "bitwidth64" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }
  it should "bitwidth128" in {
    test(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 128)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_ParallelKoggeStonePrefixSumRegistered_Random(_))
  }               
}

class Test_Emit_ParallelKoggeStonePrefixSumRegistered extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth2" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth2.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth4" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth4.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth8" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth8.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth16" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth16.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth32" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth32.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth64" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth64.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }  

  "Emit_ParallelKoggeStonePrefixSumRegistered_bitwidth128" in {
      var filename="ParallelKoggeStonePrefixSumRegistered_bitwidth128.v"
      var intersect=chisel3.getVerilogString(new ParallelKoggeStonePrefixSumRegistered(bitwidth = 128))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }    
}