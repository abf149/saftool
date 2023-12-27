import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import scala.util.Random
import java.nio.file.{Paths, Files}
import java.nio.charset.StandardCharsets
import scala.collection.mutable

class Workload_VectorDirectMappedIntersectionUnitRegistered(dut: VectorDirectMappedIntersectionUnitRegistered) extends PeekPokeTester(dut) {
  val rand = new Random

  // Adjusted to match attributes of the component instance
  val numTags = dut.vectorLength
  val maxTagValue = dut.fiberLength - 1 
  val checkOutputCorrectness = false

  def generateUniqueRandomList(size: Int, maxValue: Int): Seq[Int] = {
    val set = mutable.Set[Int]()
    while (set.size < size) {
      set += rand.nextInt(maxValue)
    }
    set.toSeq.sorted
  }

  val leftTestVector = generateUniqueRandomList(numTags, maxTagValue)
  val rightTestVector = generateUniqueRandomList(numTags, maxTagValue)

  poke(dut.io.enable, true)

  for (i <- leftTestVector.indices) {
    poke(dut.io.list1(i), leftTestVector(i))
    poke(dut.io.list2(i), rightTestVector(i))
  }

  step(15) // Allow time for processing

  if (checkOutputCorrectness) {
    val expectedResult = leftTestVector.intersect(rightTestVector).sorted.take(numTags)
    for (i <- expectedResult.indices) {
      expect(dut.io.commonElements(i), expectedResult(i))
    }
    expect(dut.io.numMatches, expectedResult.length)
  }
}

class Test_VectorDirectMappedIntersectionUnitRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "VectorDirectMappedIntersectionUnitRegistered"

  val vectorLengths = List(1, 2, 4)
  val fiberLengths = List(8, 16, 32)
  var verilog_dir = "src/verilog/"

  val combinations = for {
    vectorLength <- vectorLengths
    fiberLength <- fiberLengths
  } yield (vectorLength, fiberLength)

  def createTest(vectorLength: Int, fiberLength: Int): Unit = {
    if (fiberLength > vectorLength) {
      val tagBitWidth = log2Ceil(fiberLength)
      it should s"vectorLength${vectorLength}_fiberLength${fiberLength}_tagBitWidth${tagBitWidth}" in {
        test(new VectorDirectMappedIntersectionUnitRegistered(vectorLength, fiberLength, tagBitWidth))
          .withAnnotations(Seq(WriteVcdAnnotation))
          .runPeekPoke(new Workload_VectorDirectMappedIntersectionUnitRegistered(_))
      }
      emitVerilog(vectorLength, fiberLength, tagBitWidth)
    }
  }

  def emitVerilog(vectorLength: Int, fiberLength: Int, tagBitWidth: Int): Unit = {
    val filename = s"VectorDirectMappedIntersectionUnitRegistered_vectorLength${vectorLength}_fiberLength${fiberLength}_tagBitWidth${tagBitWidth}.v"
    val verilogString = chisel3.getVerilogString(new VectorDirectMappedIntersectionUnitRegistered(vectorLength, fiberLength, tagBitWidth))
    Files.write(Paths.get(verilog_dir + filename), verilogString.getBytes(StandardCharsets.UTF_8))
  }

  combinations.foreach { case (vectorLength, fiberLength) =>
    createTest(vectorLength, fiberLength)
  }
}