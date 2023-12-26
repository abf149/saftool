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

class Workload_VectorParallelDec2PriorityEncoderRegistered_Random(penc: VectorParallelDec2PriorityEncoderRegistered) extends PeekPokeTester(penc) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  poke(penc.io.enable, true)

  for (i <- 0 to 100) {
    poke(penc.io.input, rand.nextInt())
    step(1)
  }
}

class Test_Sim_VectorParallelDec2PriorityEncoderRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "VectorParallelDec2PriorityEncoderRegistered"
  
  it should "inputbits2_vectorLength2" in {
    test(new VectorParallelDec2PriorityEncoderRegistered(vectorLength = 4, inputbits = 8)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_VectorParallelDec2PriorityEncoderRegistered_Random(_))
  }
  // Add additional test cases for different inputbits and vectorLength values as needed
}

class Test_Emit_VectorParallelDec2PriorityEncoderRegistered extends AnyFreeSpec with ChiselScalatestTester {
  var verilog_dir = "src/verilog/"

  "Emit_VectorParallelDec2PriorityEncoderRegistered_inputbits2_vectorLength2" in {
    var filename = "VectorParallelDec2PriorityEncoderRegistered_inputbits2_vectorLength2.v"
    var intersect = chisel3.getVerilogString(new VectorParallelDec2PriorityEncoderRegistered(vectorLength = 2, inputbits = 2))
    Files.write(Paths.get(verilog_dir + filename), intersect.getBytes(StandardCharsets.UTF_8))
  }
  // Add additional test cases for emitting Verilog for different inputbits and vectorLength values as needed
}
