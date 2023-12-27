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

class Workload_BitmaskRipplePrefixSumRegistered_Random(pfsum: BitmaskRipplePrefixSumRegistered) extends PeekPokeTester(pfsum) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  for (i <- 0 to 100)
  {
    poke(pfsum.input.bitmask, rand.nextInt()) //85
    step(1)
  }
}

class Test_Sim_BitmaskRipplePrefixSumRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "BitmaskRipplePrefixSumRegistered"
  it should "bitwidth2" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }    
  it should "bitwidth4" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }    
  it should "bitwidth8" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }        
  it should "bitwidth16" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }  
  it should "bitwidth32" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }  
  it should "bitwidth64" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }
  it should "bitwidth128" in {
    test(new BitmaskRipplePrefixSumRegistered(bitwidth = 128)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_BitmaskRipplePrefixSumRegistered_Random(_))
  }               
}

class Test_Emit_BitmaskRipplePrefixSumRegistered extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth2" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth2.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth4" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth4.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth8" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth8.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth16" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth16.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth32" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth32.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth64" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth64.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }  

  "Emit_BitmaskRipplePrefixSumRegistered_bitwidth128" in {
      var filename="BitmaskRipplePrefixSumRegistered_bitwidth128.v"
      var intersect=chisel3.getVerilogString(new BitmaskRipplePrefixSumRegistered(bitwidth = 128))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }    
}
