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

class Workload_GeneralizedParallelKoggeStonePrefixSumRegistered_Random(pfsum: GeneralizedParallelKoggeStonePrefixSumRegistered) extends PeekPokeTester(pfsum) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  for (i <- 0 to 100)
  {
    // Generate a random Vec of UInt values and poke them into the input
    val randVec = Seq.fill(pfsum.vectorLength)(rand.nextInt(1 << pfsum.inputBitWidth))
    for (j <- randVec.indices) {
      poke(pfsum.input(j), randVec(j))
    }
    step(1)
  }
}

class Test_Sim_GeneralizedParallelKoggeStonePrefixSumRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "GeneralizedKoggeStonePrefixSumRegistered"
  it should "vectorLength2_inputBitWidth3" in {
    test(new GeneralizedParallelKoggeStonePrefixSumRegistered(vectorLength = 2, inputBitWidth = 3)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new Workload_GeneralizedParallelKoggeStonePrefixSumRegistered_Random(_))
  }    
  // Add additional test cases for different vectorLength and inputBitWidth values as needed
}

class Test_Emit_GeneralizedKoggeStonePrefixSumRegistered extends AnyFreeSpec with ChiselScalatestTester {

  var verilog_dir="src/verilog/"

  "Emit_GeneralizedKoggeStonePrefixSumRegistered_vectorLength2_inputBitWidth3" in {
      var filename="GeneralizedKoggeStonePrefixSumRegistered_vectorLength2_inputBitWidth3.v"
      var intersect=chisel3.getVerilogString(new GeneralizedParallelKoggeStonePrefixSumRegistered(vectorLength = 2, inputBitWidth = 3))
      Files.write(Paths.get(verilog_dir+filename), intersect.getBytes(StandardCharsets.UTF_8))      
  }

  // Add additional emit cases for different vectorLength and inputBitWidth values as needed
}
