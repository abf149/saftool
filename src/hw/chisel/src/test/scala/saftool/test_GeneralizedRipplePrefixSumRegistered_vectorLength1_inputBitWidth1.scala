import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import java.nio.file.{Files, Paths, StandardOpenOption}
import java.nio.charset.StandardCharsets

class Workload_GeneralizedRipplePrefixSumRegistered_Random(pfsum: GeneralizedRipplePrefixSumRegistered) extends PeekPokeTester(pfsum) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  for (i <- 0 to 100) {
    // Generate a random Vec of UInt values and poke them into the input
    val randVec = Seq.fill(pfsum.vectorLength)(rand.nextInt(1 << pfsum.inputBitWidth))
    for (j <- randVec.indices) {
      poke(pfsum.input(j), randVec(j))
    }
    step(1)
  }
}

class Test_Sim_GeneralizedRipplePrefixSumRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "GeneralizedRipplePrefixSumRegistered"

  val chiselTestDir = sys.env.getOrElse("CHISEL_TEST_DIR", "src/test/scala/saftool") // Default path if the environment variable is not set
  var verilog_dir = "src/verilog/"

  // Phase 1: inputBitWidth of 1 with specific vectorLength values
  val vectorLengthsPhase1 = List(1, 2, 4, 8, 16, 32, 64)
  val inputBitWidthsPhase1 = List(1)

  // Phase 2: Cartesian product of inputBitWidth [2,4,8] and vectorLength [1,2,4,8,16]
  val vectorLengthsPhase2 = List(1, 2, 4, 8, 16)
  val inputBitWidthsPhase2 = List(2, 4, 8)

  val combinations = (vectorLengthsPhase1.map(vl => (vl, 1)) ++ product(vectorLengthsPhase2, inputBitWidthsPhase2)).distinct

  def createTest(vectorLength: Int, inputBitWidth: Int): Unit = {
    val testName = s"test_GeneralizedRipplePrefixSumRegistered_vectorLength${vectorLength}_inputBitWidth${inputBitWidth}.scala"
    val testFilePath = Paths.get(chiselTestDir, testName)

    if (!Files.exists(testFilePath)) {
      Files.createFile(testFilePath)
    }

    it should s"vectorLength${vectorLength}_inputBitWidth${inputBitWidth}" in {
      test(new GeneralizedRipplePrefixSumRegistered(vectorLength, inputBitWidth))
        .withAnnotations(Seq(WriteVcdAnnotation))
        .runPeekPoke(new Workload_GeneralizedRipplePrefixSumRegistered_Random(_))
    }
    emitVerilog(vectorLength, inputBitWidth)
  }

  def emitVerilog(vectorLength: Int, inputBitWidth: Int): Unit = {
    val filename = s"GeneralizedRipplePrefixSumRegistered_vectorLength${vectorLength}_inputBitWidth${inputBitWidth}.v"
    val verilogString = chisel3.getVerilogString(new GeneralizedRipplePrefixSumRegistered(vectorLength, inputBitWidth))
    Files.write(Paths.get(verilog_dir + filename), verilogString.getBytes(StandardCharsets.UTF_8))
  }

  combinations.foreach { case (vectorLength, inputBitWidth) =>
    createTest(vectorLength, inputBitWidth)
  }

  private def product[A, B](listA: List[A], listB: List[B]): List[(A, B)] = {
    for {
      a <- listA
      b <- listB
    } yield (a, b)
  }
}