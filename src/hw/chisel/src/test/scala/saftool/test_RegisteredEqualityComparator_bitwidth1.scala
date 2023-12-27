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

class Workload_RegisteredEqualityComparator_Random(registeredeqcomparator: RegisteredEqualityComparator) extends PeekPokeTester(registeredeqcomparator) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  //var j=0
  for (i <- 0 to 10000)
  {
    poke(registeredeqcomparator.io.inL,rand.nextInt()) //85
    poke(registeredeqcomparator.io.inR,rand.nextInt()) //205 
    step(1)
  }
}

class Test_Sim_RegisteredEqualityComparator extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "RegisteredEqualityComparator"
  it should "bitwidth1" in {
    test(new RegisteredEqualityComparator(bitwidth = 1)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }  
  it should "bitwidth2" in {
    test(new RegisteredEqualityComparator(bitwidth = 2)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }  
  it should "bitwidth4" in {
    test(new RegisteredEqualityComparator(bitwidth = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }  
  it should "bitwidth8" in {
    test(new RegisteredEqualityComparator(bitwidth = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }    
  it should "bitwidth16" in {
    test(new RegisteredEqualityComparator(bitwidth = 16)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }  
  it should "bitwidth32" in {
    test(new RegisteredEqualityComparator(bitwidth = 32)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }  
  it should "bitwidth64" in {
    test(new RegisteredEqualityComparator(bitwidth = 64)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_RegisteredEqualityComparator_Random(_))
  }              
}

class Test_Emit_RegisteredEqualityComparator extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_RegisteredEqualityComparator_bitwidth1" in {
      var filename="RegisteredEqualityComparator_bitwidth1.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 1))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredEqualityComparator_bitwidth2" in {
      var filename="RegisteredEqualityComparator_bitwidth2.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 2))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredEqualityComparator_bitwidth4" in {
      var filename="RegisteredEqualityComparator_bitwidth4.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 4))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredEqualityComparator_bitwidth8" in {
      var filename="RegisteredEqualityComparator_bitwidth8.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 8))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredEqualityComparator_bitwidth16" in {
      var filename="RegisteredEqualityComparator_bitwidth16.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 16))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredEqualityComparator_bitwidth32" in {
      var filename="RegisteredEqualityComparator_bitwidth32.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 32))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  "Emit_RegisteredEqualityComparator_bitwidth64" in {
      var filename="RegisteredEqualityComparator_bitwidth64.v"
      var intersect=chisel3.getVerilogString(new RegisteredEqualityComparator(bitwidth = 64))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }  
}