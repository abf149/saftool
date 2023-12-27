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

class Workload_RegisteredMultiplier_Random(registeredmultiplier: RegisteredMultiplier) extends PeekPokeTester(registeredmultiplier) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  //var j=0
  for (i <- 0 to 10000)
  {
    poke(registeredmultiplier.io.inL,rand.nextInt()) //85
    poke(registeredmultiplier.io.inR,rand.nextInt()) //205 
    step(1)
  }
}

class Test_Sim_RegisteredMultiplier extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "RegisteredMultiplier"
  it should "bitwidth1" in {
    test(new RegisteredMultiplier(bitwidth = 1)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }  
  it should "bitwidth2" in {
    test(new RegisteredMultiplier(bitwidth = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }  
  it should "bitwidth4" in {
    test(new RegisteredMultiplier(bitwidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }  
  it should "bitwidth8" in {
    test(new RegisteredMultiplier(bitwidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }    
  it should "bitwidth16" in {
    test(new RegisteredMultiplier(bitwidth = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }  
  it should "bitwidth32" in {
    test(new RegisteredMultiplier(bitwidth = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }  
  it should "bitwidth64" in {
    test(new RegisteredMultiplier(bitwidth = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredMultiplier_Random(_))
  }              
}

class Test_Emit_RegisteredMultiplier extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_RegisteredMultiplier_bitwidth1" in {
      var filename="RegisteredMultiplier_bitwidth1.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 1))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredMultiplier_bitwidth2" in {
      var filename="RegisteredMultiplier_bitwidth2.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredMultiplier_bitwidth4" in {
      var filename="RegisteredMultiplier_bitwidth4.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredMultiplier_bitwidth8" in {
      var filename="RegisteredMultiplier_bitwidth8.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredMultiplier_bitwidth16" in {
      var filename="RegisteredMultiplier_bitwidth16.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredMultiplier_bitwidth32" in {
      var filename="RegisteredMultiplier_bitwidth32.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredMultiplier_bitwidth64" in {
      var filename="RegisteredMultiplier_bitwidth64.v"
      var intersect=chisel3.getVerilogString(new RegisteredMultiplier(bitwidth = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }  
}